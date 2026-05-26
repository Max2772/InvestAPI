from datetime import datetime, timezone

import aiohttp

from app.config import CRYPTO_HISTORY_PERIOD, REDIS_CRYPTO_HISTORY_INTERVAL, CRYPTO_PROVIDER_NAME
from app.database import RedisClient
from app.schemas.history_responses import CryptoHistoryResponse, HistoryPoint
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.crypto_parser import resolve_crypto_coin
from app.utils.history_points import (
    collapse_to_daily,
    filter_points_by_days,
)
from app.utils.logging import logger


def _slice_cached(cached: CryptoHistoryResponse, coin: str, days: int) -> CryptoHistoryResponse:
    points = filter_points_by_days(cached.points, days)
    if not points:
        raise AssetNotFoundError(f"Cryptocurrency history for {coin} not found")
    return CryptoHistoryResponse(
        name=coin,
        points=points,
        cached_at=cached.cached_at,
    )


async def _fetch_history(
    coin: str,
    http_session: aiohttp.ClientSession,
) -> list[HistoryPoint]:
    logger.info(
        f"Fetching crypto history for {coin} ({CRYPTO_HISTORY_PERIOD} days) "
        f"from {CRYPTO_PROVIDER_NAME}"
    )
    url = (
        "https://api.coingecko.com/api/v3/coins/"
        f"{coin}/market_chart?vs_currency=usd&days={CRYPTO_HISTORY_PERIOD}"
    )

    async with http_session.get(url) as response:
        data = await response.json()
        response.raise_for_status()

    prices = data.get("prices")
    if not prices:
        raise AssetNotFoundError(f"Cryptocurrency history for {coin} not found")

    volumes_by_ts: dict[int, float] = {}
    for entry in data.get("total_volumes") or []:
        if len(entry) >= 2 and entry[1] is not None:
            volumes_by_ts[int(entry[0])] = float(entry[1])

    points: list[HistoryPoint] = []
    for entry in prices:
        if len(entry) < 2 or entry[1] is None:
            continue
        ts_ms = int(entry[0])
        points.append(
            HistoryPoint(
                timestamp=datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).replace(
                    tzinfo=None
                ),
                price=round(float(entry[1]), 4),
                volume=round(volumes_by_ts[ts_ms], 4) if ts_ms in volumes_by_ts else None,
            )
        )

    points = collapse_to_daily(points)
    if not points:
        raise AssetNotFoundError(f"Cryptocurrency history for {coin} not found")
    return points


async def get_crypto_history(
    coin: str,
    days: int,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> CryptoHistoryResponse:
    coin = resolve_crypto_coin(coin)
    cache_key = f"coin:history:{coin}"

    if redis_client:
        cached = await redis_client.get_cache(cache_key, CryptoHistoryResponse)
        if cached and cached.points:
            return _slice_cached(cached, coin, days)

    try:
        points = await _fetch_history(coin, http_session)
        cached_at = datetime.now()

        full_response = CryptoHistoryResponse(
            name=coin,
            points=points,
            cached_at=cached_at,
        )

        if redis_client:
            await redis_client.set_cache(
                cache_key, full_response, REDIS_CRYPTO_HISTORY_INTERVAL
            )

        return _slice_cached(full_response, coin, days)
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto history for {coin}: {e}")
        raise handle_error_exception(e, source=CRYPTO_PROVIDER_NAME) from e
