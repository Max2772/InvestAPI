import pytest
from fastapi import HTTPException

from app.schemas import SteamResponse
from app.services.steam_price import get_steam_item_price
from app.utils import AssetNotFoundError, ExternalServiceError
from tests.conftest import FakeAiohttpResponse, sample_steam


@pytest.mark.asyncio
async def test_steam_uses_lowest_price(fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse(
            {"success": True, "lowest_price": "$1.50", "median_price": "$2.00"}
        )
    )

    result = await get_steam_item_price(730, "Test Case", None, session)

    assert isinstance(result, SteamResponse)
    assert result.price == 1.5


@pytest.mark.asyncio
async def test_steam_falls_back_to_median_price(fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse({"success": True, "median_price": "$2.01"})
    )

    result = await get_steam_item_price(730, "CS20 Case", None, session)

    assert isinstance(result, SteamResponse)
    assert result.price == 2.01


@pytest.mark.asyncio
async def test_steam_parses_non_dollar_price(fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse({"success": True, "lowest_price": "CDN$ 14.97"})
    )

    result = await get_steam_item_price(730, "CDN Case", None, session)

    assert result.price == 14.97


@pytest.mark.asyncio
async def test_steam_not_found_when_no_prices(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"success": True}))

    with pytest.raises(AssetNotFoundError, match="Steam item price not found"):
        await get_steam_item_price(730, "Unknown", None, session)


@pytest.mark.asyncio
async def test_steam_bad_gateway_when_success_false(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"success": False}))

    with pytest.raises(ExternalServiceError, match="success == False"):
        await get_steam_item_price(730, "Bad", None, session)


@pytest.mark.asyncio
async def test_steam_returns_cache_without_http_call(
    redis_client, sample_steam, fake_http_session
):
    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=AssertionError("HTTP must not be called"))
    )
    await redis_client.set_cache("steam:730:Glove Case", sample_steam, ttl=900)

    result = await get_steam_item_price(730, "Glove Case", redis_client, session)

    assert result == sample_steam


@pytest.mark.asyncio
async def test_steam_network_error_raises_http_exception(fake_http_session):
    import aiohttp

    session = fake_http_session(
        FakeAiohttpResponse(
            {},
            raise_for_status=aiohttp.ClientConnectionError("connection refused"),
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_steam_item_price(730, "Case", None, session)

    assert exc_info.value.status_code == 503
