import re
from datetime import datetime
from urllib.parse import quote

import aiohttp

from app.config import STEAM_PROVIDER_NAME
from app.database import RedisClient
from app.schemas import SteamResponse
from app.utils import AssetNotFoundError, ExternalServiceError, handle_error_exception
from app.utils.logging import logger


async def _fetch_steam_price(
        app_id: int,
        market_hash_name: str,
        http_session: aiohttp.ClientSession
) -> SteamResponse:
    logger.info(
        f"Fetching steam item {market_hash_name}, app_id={app_id} from {STEAM_PROVIDER_NAME}"
    )
    url = (
        "https://steamcommunity.com/market/priceoverview/"
        f"?appid={app_id}&market_hash_name={quote(market_hash_name)}&currency=1"
    )

    async with http_session.get(url) as response:
        data = await response.json()
        response.raise_for_status()

    if not data.get("success"):
        raise ExternalServiceError("success == False")

    lowest_price = data.get("lowest_price")
    median_price = data.get("median_price")
    if lowest_price is None and median_price is None:
        raise AssetNotFoundError("Steam item price not found")

    price = lowest_price if lowest_price else median_price
    clean_price = float(re.sub(r"[^\d.]", "", price))

    return SteamResponse(
        app_id=app_id,
        name=market_hash_name,
        price=clean_price,
        currency="USD",
        cached_at=datetime.now(),
    )


async def get_steam_item_price(
    app_id: int,
    market_hash_name: str,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> SteamResponse:
    cache_key = f"steam:{app_id}:{market_hash_name}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key)
        if cache:
            return cache

    try:
        response_data = await _fetch_steam_price(
            app_id,
            market_hash_name,
            http_session
        )

        if redis_client:
            await redis_client.set_cache(cache_key, response_data)

        return response_data
    except (AssetNotFoundError, ExternalServiceError):
        raise
    except Exception as e:
        logger.error(
            f"Error fetching steam item {market_hash_name}, app_id={app_id}: {e}"
        )
        raise handle_error_exception(e, source=STEAM_PROVIDER_NAME) from e
