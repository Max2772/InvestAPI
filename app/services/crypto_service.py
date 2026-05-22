from datetime import datetime

import aiohttp

from app.database import RedisClient
from app.schemas import CryptoResponse
from app.types.constants import CRYPTO_SYMBOLS
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.logging import logger


async def get_crypto_price(
    coin: str,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> CryptoResponse:
    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()
    cache_key = f"coin:{coin}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key)
        if cache:
            return cache

    try:
        logger.info(f"Fetching coin data for {coin} from CoinGecko API")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"

        async with http_session.get(url) as response:
            data = await response.json()
            response.raise_for_status()

        coin_data = data.get(coin)
        if not coin_data or "usd" not in coin_data:
            raise AssetNotFoundError(f"Cryptocurrency {coin} not found")

        price = coin_data.get("usd")
        if price is None or not isinstance(price, (int, float)):
            raise AssetNotFoundError(f"Price for cryptocurrency {coin} not available")

        response_data = CryptoResponse(
            name=coin,
            price=round(price, 2),
            currency="USD",
            source="CoinGecko",
            cached_at=datetime.now(),
        )

        if redis_client:
            await redis_client.set_cache(cache_key, response_data)

        return response_data
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto {coin}: {e}")
        raise handle_error_exception(e, source="CoinGecko API") from e
