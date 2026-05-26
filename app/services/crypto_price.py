from datetime import datetime

import aiohttp

from app.config import CRYPTO_PROVIDER_NAME, REDIS_CRYPTO_INTERVAL
from app.database import RedisClient
from app.schemas import CryptoResponse
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.crypto_parser import ResolvedCrypto, resolve_crypto_coin
from app.utils.logging import logger


async def _fetch_crypto_price(
    coin: ResolvedCrypto,
    http_session: aiohttp.ClientSession,
) -> CryptoResponse:
    logger.info(f"Fetching coin data for {coin.id} from {CRYPTO_PROVIDER_NAME}")
    url = (
        "https://api.coingecko.com/api/v3/simple/"
        f"price?ids={coin.id}&vs_currencies=usd"
    )

    async with http_session.get(url) as response:
        data = await response.json()
        response.raise_for_status()

    coin_data = data.get(coin.id)
    if not coin_data or "usd" not in coin_data:
        raise AssetNotFoundError(f"Cryptocurrency {coin.id} not found")

    price = coin_data.get("usd")
    if price is None or not isinstance(price, (int, float)):
        raise AssetNotFoundError(f"Price for cryptocurrency {coin.id} not available")

    return CryptoResponse(
        name=coin.id,
        symbol=coin.symbol,
        full_name=coin.full_name,
        price=round(price, 2),
        currency="USD",
        cached_at=datetime.now(),
    )


async def get_crypto_price(
    coin: str,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> CryptoResponse:
    coin: ResolvedCrypto = resolve_crypto_coin(coin)
    cache_key = f"coin:{coin.id}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key, CryptoResponse)
        if cache:
            return cache

    try:
        response_data = await _fetch_crypto_price(coin, http_session)

        if redis_client:
            await redis_client.set_cache(cache_key, response_data, REDIS_CRYPTO_INTERVAL)

        return response_data
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto {coin.id}: {e}")
        raise handle_error_exception(e, source=CRYPTO_PROVIDER_NAME) from e
