import asyncio
from datetime import datetime

import aiohttp

from app.config import REDIS_CRYPTO_INTERVAL, CRYPTO_PROVIDER_NAME
from app.database import RedisClient
from app.schemas import CryptoResponse
from app.types.constants.crypto_symbols import CRYPTO_COINS
from app.utils.crypto_parser import resolve_crypto_coin
from app.utils.logging import logger

CRYPTO_CACHE_REFRESH_SECONDS = 15 * 60
CACHE_COIN_LIMIT = 250


def crypto_prices_cache_url() -> str:
    url = "https://api.coingecko.com/api/v3/simple/price?ids={coins}&vs_currencies=usd"
    coins = [name_id for name_id, symbol, full_name in CRYPTO_COINS]

    return url.format(coins=",".join(coins[:CACHE_COIN_LIMIT]))


async def _refresh_crypto_cache_once(
        redis_client: RedisClient | None,
        http_session: aiohttp.ClientSession,
) -> None:
    if not redis_client:
        logger.info("Skip crypto cache refresh: Redis is disabled")
        return

    async with http_session.get(crypto_prices_cache_url()) as response:
        data = await response.json()
        response.raise_for_status()

    ttl = max(REDIS_CRYPTO_INTERVAL, CRYPTO_CACHE_REFRESH_SECONDS)
    cached_at = datetime.now()

    for coin_id, coin_data in data.items():
        if not coin_data or "usd" not in coin_data:
            continue

        price = coin_data.get("usd")
        if price is None or not isinstance(price, (int, float)):
            continue

        resolved = resolve_crypto_coin(coin_id)

        await redis_client.set_cache(
            f"coin:{coin_id}",
            CryptoResponse(
                name=resolved.id,
                symbol=resolved.symbol,
                full_name=resolved.full_name,
                price=round(price, 2),
                cached_at=cached_at,
            ),
            ttl=ttl,
        )

    logger.info(f"Crypto cache refreshed (bulk {CRYPTO_PROVIDER_NAME})")


async def crypto_cache_refresh_loop(
        *,
        redis_client: RedisClient | None,
        http_session: aiohttp.ClientSession,
) -> None:
    await asyncio.sleep(CRYPTO_CACHE_REFRESH_SECONDS)

    while True:
        try:
            await _refresh_crypto_cache_once(redis_client, http_session)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Crypto cache refresh failed: {e}")
        finally:
            await asyncio.sleep(CRYPTO_CACHE_REFRESH_SECONDS)
