from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.schemas.history_responses import SteamHistoryResponse
from app.services.steam_history import get_steam_item_history
from app.utils import AssetNotFoundError
from tests.conftest import FakeAiohttpResponse, sample_steam_history
from tests.test_steam_history_parser import SSR_HTML

RECENT_SSR_HTML = SSR_HTML.replace("1716508800", str(int(datetime.now().timestamp())))
RECENT_SSR_HTML = RECENT_SSR_HTML.replace(
    "1716595200", str(int((datetime.now() - timedelta(days=1)).timestamp()))
)


@pytest.mark.asyncio
async def test_steam_history_success(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse(RECENT_SSR_HTML))

    result = await get_steam_item_history(730, "Glove Case", 90, None, session)

    assert isinstance(result, SteamHistoryResponse)
    assert result.app_id == 730
    assert result.name == "Glove Case"
    assert len(result.points) >= 1


@pytest.mark.asyncio
async def test_steam_history_not_found(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse("<html></html>"))

    with pytest.raises(AssetNotFoundError, match="Steam item history for Unknown not found"):
        await get_steam_item_history(730, "Unknown", 30, None, session)


@pytest.mark.asyncio
async def test_steam_history_cache_hit(redis_client, sample_steam_history, fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse("", raise_for_status=AssertionError("HTTP must not be called"))
    )
    await redis_client.set_model_cache(
        "steam:history:730:Glove Case",
        sample_steam_history,
        ttl=900,
    )

    result = await get_steam_item_history(730, "Glove Case", 30, redis_client, session)

    assert result.name == "Glove Case"
    assert result.interval == "1d"
    assert result.cached_at == sample_steam_history.cached_at


@pytest.mark.asyncio
async def test_steam_history_network_error(fake_http_session):
    import aiohttp

    session = fake_http_session(
        FakeAiohttpResponse(
            "",
            raise_for_status=aiohttp.ClientConnectionError("connection refused"),
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_steam_item_history(730, "Case", 30, None, session)

    assert exc_info.value.status_code == 503
