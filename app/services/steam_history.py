from datetime import datetime
from urllib.parse import quote

import aiohttp

from app.config import REDIS_STEAM_HISTORY_INTERVAL, STEAM_PROVIDER_NAME
from app.database import RedisClient
from app.schemas.history_responses import SteamHistoryResponse, HistoryPoint
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.history_points import (
    DAILY_INTERVAL,
    collapse_to_daily,
    filter_points_by_days,
)
from app.utils.logging import logger
from app.utils.steam_history_parser import parse_steam_listing_html

STEAM_LISTING_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _slice_cached(
        cached: SteamHistoryResponse,
        app_id: int,
        market_hash_name: str,
        days: int
) -> SteamHistoryResponse:
    points = filter_points_by_days(cached.points, days)
    if not points:
        raise AssetNotFoundError(f"Steam item history for {market_hash_name} not found")
    return SteamHistoryResponse(
        app_id=app_id,
        name=market_hash_name,
        points=points,
        cached_at=cached.cached_at,
    )

async def _fetch_history(
        app_id: int,
        market_hash_name: str,
        http_session: aiohttp.ClientSession,
) -> SteamHistoryResponse:
    url = (
        "https://steamcommunity.com/market/listings/"
        f"{app_id}/{quote(market_hash_name)}"
    )
    logger.info(
        f"Fetching steam history for {market_hash_name}, app_id={app_id} "
        f"from {STEAM_PROVIDER_NAME} listing page"
    )

    async with http_session.get(url, headers=STEAM_LISTING_HEADERS) as response:
        html = await response.text()
        response.raise_for_status()

    points = collapse_to_daily(parse_steam_listing_html(html))
    if not points:
        raise AssetNotFoundError(
            f"Steam item history for {market_hash_name} not found"
        )

    return SteamHistoryResponse(
        app_id=app_id,
        name=market_hash_name,
        interval=DAILY_INTERVAL,
        points=points,
        cached_at=datetime.now(),
    )


async def get_steam_item_history(
    app_id: int,
    market_hash_name: str,
    days: int,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> SteamHistoryResponse:
    cache_key = f"steam:history:{app_id}:{market_hash_name}"

    if redis_client:
        cached = await redis_client.get_cache(cache_key, SteamHistoryResponse)
        if cached and cached.points:
            return _slice_cached(cached, app_id, market_hash_name, days)

    try:
        full_response = await _fetch_history(app_id, market_hash_name, http_session)

        if redis_client:
            await redis_client.set_cache(
                cache_key, full_response, REDIS_STEAM_HISTORY_INTERVAL
            )

        return _slice_cached(full_response, app_id, market_hash_name, days)
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching steam history for {market_hash_name}, app_id={app_id}: {e}"
        )
        raise handle_error_exception(e, source=STEAM_PROVIDER_NAME) from e
