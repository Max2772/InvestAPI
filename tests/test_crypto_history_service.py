from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.config import CRYPTO_HISTORY_PERIOD
from app.schemas.history_responses import CryptoHistoryResponse, HistoryPoint
from app.services.crypto_history import get_crypto_history
from app.utils import AssetNotFoundError
from tests.conftest import FakeAiohttpGetCtx, FakeAiohttpResponse


def _recent_market_chart_payload() -> dict:
    now_ms = int(datetime.now().timestamp() * 1000)
    day_ms = 86_400_000
    return {
        "prices": [[now_ms - day_ms, 145.5], [now_ms, 146.2]],
        "total_volumes": [[now_ms - day_ms, 1_000_000.0], [now_ms, 1_100_000.0]],
    }


@pytest.mark.asyncio
async def test_crypto_history_success(fake_http_session):
    payload = _recent_market_chart_payload()
    session = fake_http_session(FakeAiohttpResponse(payload))

    result = await get_crypto_history("solana", 30, None, session)

    assert isinstance(result, CryptoHistoryResponse)
    assert result.name == "solana"
    assert result.symbol == "SOL"
    assert result.full_name == "Solana"
    assert result.interval == "1d"
    assert len(result.points) == 2
    assert result.points[0].price == 145.5


@pytest.mark.asyncio
async def test_crypto_history_fetches_max_days(fake_http_session):
    captured: dict[str, str] = {}

    class TrackingSession:
        def get(self, url: str, **_kwargs: object) -> FakeAiohttpGetCtx:
            captured["url"] = url
            now_ms = int(datetime.now().timestamp() * 1000)
            return FakeAiohttpGetCtx(
                FakeAiohttpResponse(
                    {
                        "prices": [[now_ms, 10.0]],
                        "total_volumes": [],
                    }
                )
            )

    await get_crypto_history("solana", 7, None, TrackingSession())

    assert f"days={CRYPTO_HISTORY_PERIOD}" in captured["url"]


@pytest.mark.asyncio
async def test_crypto_history_symbol_alias(fake_http_session):
    now_ms = int(datetime.now().timestamp() * 1000)
    payload = {
        "prices": [[now_ms, 10.0]],
        "total_volumes": [],
    }
    session = fake_http_session(FakeAiohttpResponse(payload))

    result = await get_crypto_history("SOL", 7, None, session)

    assert result.name == "solana"
    assert result.symbol == "SOL"


@pytest.mark.asyncio
async def test_crypto_history_not_found(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"prices": []}))

    with pytest.raises(
        AssetNotFoundError, match="Cryptocurrency history for unknowncoin not found"
    ):
        await get_crypto_history("unknowncoin", 30, None, session)


@pytest.mark.asyncio
async def test_crypto_history_cache_hit_without_http(
    redis_client, fake_http_session
):
    old_ts = datetime.now() - timedelta(days=60)
    recent_ts = datetime.now() - timedelta(days=5)
    cached = CryptoHistoryResponse(
        name="solana",
        symbol="SOL",
        full_name="Solana",
        interval="1d",
        points=[
            HistoryPoint(timestamp=old_ts, price=100.0, volume=1.0),
            HistoryPoint(timestamp=recent_ts, price=145.5, volume=2.0),
        ],
        cached_at=datetime(2026, 5, 22, 12, 0, 0),
    )
    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=AssertionError("HTTP must not be called"))
    )
    await redis_client.set_cache("coin:history:solana", cached, ttl=600)

    result = await get_crypto_history("solana", 30, redis_client, session)

    assert result.name == "solana"
    assert len(result.points) == 1
    assert result.points[0].price == 145.5
    assert result.cached_at == cached.cached_at


@pytest.mark.asyncio
async def test_crypto_history_http_error(fake_http_session):
    import aiohttp

    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=aiohttp.ServerTimeoutError("timeout"))
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_crypto_history("solana", 30, None, session)

    assert exc_info.value.status_code == 504
