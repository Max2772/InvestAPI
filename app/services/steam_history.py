from datetime import datetime, timedelta
from urllib.parse import quote

import aiohttp

from app.config import REDIS_STEAM_HISTORY_INTERVAL
from app.database import RedisClient
from app.schemas.history_responses import HistoryPoint, SteamHistoryResponse
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.logging import logger
from app.utils.steam_history_parser import parse_steam_listing_html

STEAM_LISTING_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _filter_points_by_days(points: list[HistoryPoint], days: int) -> list[HistoryPoint]:
    cutoff = datetime.now() - timedelta(days=days)
    return [point for point in points if point.timestamp >= cutoff]


async def get_steam_item_history(
    app_id: int,
    market_hash_name: str,
    days: int,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> SteamHistoryResponse:
    cache_key = f"steam:history:{app_id}:{market_hash_name}:{days}"

    if redis_client:
        cache = await redis_client.get_model_cache(cache_key, SteamHistoryResponse)
        if cache:
            return cache

    try:
        listing_url = (
            "https://steamcommunity.com/market/listings/"
            f"{app_id}/{quote(market_hash_name)}"
        )
        logger.info(
            f"Fetching steam history for {market_hash_name}, app_id={app_id} "
            f"from listing page"
        )

        async with http_session.get(listing_url, headers=STEAM_LISTING_HEADERS) as response:
            html = await response.text()
            response.raise_for_status()

        points = parse_steam_listing_html(html)
        if not points:
            raise AssetNotFoundError(
                f"Steam item history for {market_hash_name} not found"
            )

        points = _filter_points_by_days(points, days)
        if not points:
            raise AssetNotFoundError(
                f"Steam item history for {market_hash_name} not found"
            )

        response_data = SteamHistoryResponse(
            app_id=app_id,
            name=market_hash_name,
            points=points,
            cached_at=datetime.now(),
        )

        if redis_client:
            await redis_client.set_model_cache(
                cache_key, response_data, REDIS_STEAM_HISTORY_INTERVAL
            )

        return response_data
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching steam history for {market_hash_name}, app_id={app_id}: {e}"
        )
        raise handle_error_exception(e, source=SteamHistoryResponse.source) from e
