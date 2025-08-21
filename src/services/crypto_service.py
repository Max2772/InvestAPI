import json
import aiohttp
from datetime import datetime
from fastapi.responses import JSONResponse

from src.models.price_response import CryptoResponse
from src.utils import handle_error_exception, redis_client, CRYPTO_SYMBOLS, get_logger


logger = get_logger()

async def get_crypto_price(coin: str):
    logger.info(f"Requesting price for crypto: {coin}")
    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()

#    if not coin or not isinstance(coin, str) or not coin.strip():
#        return JSONResponse(
#            status_code=400,
#            content={"error": "Bad Request", "detail": "Invalid or empty coin symbol"}
#        )

    cache_key = f"coin:{coin}"
    cached = None
    if redis_client is not None:
        cached = await redis_client.get(cache_key)

    if cached:
        logger.info(f"Found cached coin:{coin} from redis")
        return CryptoResponse(**json.loads(cached))

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        logger.info("Requesting price from Coingecko")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                price = data.get(coin, {}).get("usd")
                logger.info(f"Price successfully retrieved: ${price:.2f}")
                if price is None:
                    logger.warning(f"Cryptocurrency {coin} not found in CoinGecko response")
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Not Found", "detail": f"Cryptocurrency {coin} not found"}
                    )

                response_data = CryptoResponse(
                    name=coin,
                    price=round(price, 2),
                    currency="USD",
                    source="CoinGecko",
                    cached_at=datetime.now()
                )

                if redis_client is not None:
                    await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
                    logger.debug(f"Cached data for crypto:{coin} for 900 seconds")

                logger.info(f"Price for {coin} retrieved: ${price:.2f}")
                return response_data
    except Exception as e:
        logger.error(f"Error while parsing from CoinGecko API for {coin}: {str(e)}")
        raise handle_error_exception(e, source="CoinGecko API")