import pytest
from fastapi import HTTPException

from app.schemas.history_responses import CryptoHistoryResponse
from app.services.crypto_history import get_crypto_history
from app.utils import AssetNotFoundError
from tests.conftest import FakeAiohttpResponse, sample_crypto_history


@pytest.mark.asyncio
async def test_crypto_history_success(fake_http_session):
    payload = {
        "prices": [[1714521600000, 145.5], [1714608000000, 146.2]],
        "total_volumes": [[1714521600000, 1_000_000.0], [1714608000000, 1_100_000.0]],
    }
    session = fake_http_session(FakeAiohttpResponse(payload))

    result = await get_crypto_history("solana", 30, None, session)

    assert isinstance(result, CryptoHistoryResponse)
    assert result.name == "solana"
    assert len(result.points) == 2
    assert result.points[0].price == 145.5
    assert result.points[0].volume == 1_000_000.0


@pytest.mark.asyncio
async def test_crypto_history_symbol_alias(fake_http_session):
    payload = {
        "prices": [[1714521600000, 10.0]],
        "total_volumes": [],
    }
    session = fake_http_session(FakeAiohttpResponse(payload))

    result = await get_crypto_history("SOL", 7, None, session)

    assert result.name == "solana"


@pytest.mark.asyncio
async def test_crypto_history_not_found(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"prices": []}))

    with pytest.raises(
        AssetNotFoundError, match="Cryptocurrency history for unknowncoin not found"
    ):
        await get_crypto_history("unknowncoin", 30, None, session)


@pytest.mark.asyncio
async def test_crypto_history_cache_hit(
    redis_client, sample_crypto_history, fake_http_session
):
    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=AssertionError("HTTP must not be called"))
    )
    await redis_client.set_model_cache(
        "coin:history:solana:30",
        sample_crypto_history,
        ttl=600,
    )

    result = await get_crypto_history("solana", 30, redis_client, session)

    assert result == sample_crypto_history


@pytest.mark.asyncio
async def test_crypto_history_http_error(fake_http_session):
    import aiohttp

    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=aiohttp.ServerTimeoutError("timeout"))
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_crypto_history("solana", 30, None, session)

    assert exc_info.value.status_code == 504
