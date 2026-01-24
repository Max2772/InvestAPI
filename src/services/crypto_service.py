from datetime import datetime
from typing import Union

import aiohttp
from fastapi.responses import JSONResponse

from src.logger import logger
from src.models.asset_responses import CryptoResponse
from src.utils import handle_error_exception, CRYPTO_SYMBOLS
from src.utils.redis_client import RedisClient


async def get_crypto_price(
        coin: str,
        redis_client: RedisClient
) -> Union[CryptoResponse, JSONResponse]:
    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()
    cache_key = f"coin:{coin}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key)
        if cache:
            return cache

    try:
        logger.info(f"Fetching coin data for {coin} from CoinGecko API")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                response.raise_for_status()

            coin_data = data.get(coin)
            if not coin_data or 'usd' not in coin_data:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Not Found", "detail": f"Cryptocurrency {coin} not found"}
                )

            price = coin_data.get('usd')
            if price is None or not isinstance(price, (int, float)):
                return JSONResponse(
                    status_code=404,
                    content={"error": "Not Found", "detail": f"Price for cryptocurrency {coin} not available"}
                )

            response_data = CryptoResponse(
                name=coin,
                price=round(price, 2),
                currency="USD",
                source="CoinGecko",
                cached_at=datetime.now()
            )

            if redis_client:
                await redis_client.set_cache(cache_key, response_data)

            return response_data
    except Exception as e:
        logger.error(f"Error fetching crypto {coin}: {e}")
        raise handle_error_exception(e, source="CoinGecko API")