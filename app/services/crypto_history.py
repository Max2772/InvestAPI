from datetime import datetime, timezone

import aiohttp

from app.config import REDIS_CRYPTO_HISTORY_INTERVAL
from app.database import RedisClient
from app.schemas.history_responses import CryptoHistoryResponse, HistoryPoint
from app.types.constants import CRYPTO_SYMBOLS
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.logging import logger


async def get_crypto_history(
    coin: str,
    days: int,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> CryptoHistoryResponse:
    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()
    cache_key = f"coin:history:{coin}:{days}"

    if redis_client:
        cache = await redis_client.get_model_cache(cache_key, CryptoHistoryResponse)
        if cache:
            return cache

    try:
        logger.info(f"Fetching crypto history for {coin} ({days} days) from CoinGecko API")
        url = (
            "https://api.coingecko.com/api/v3/coins/"
            f"{coin}/market_chart?vs_currency=usd&days={days}"
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

        if not points:
            raise AssetNotFoundError(f"Cryptocurrency history for {coin} not found")

        response_data = CryptoHistoryResponse(
            name=coin,
            points=points,
            cached_at=datetime.now(),
        )

        if redis_client:
            await redis_client.set_model_cache(
                cache_key, response_data, REDIS_CRYPTO_HISTORY_INTERVAL
            )

        return response_data
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto history for {coin}: {e}")
        raise handle_error_exception(e, source=CryptoHistoryResponse.source) from e
