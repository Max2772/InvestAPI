import json
import httpx
from datetime import datetime
from fastapi.responses import JSONResponse
import redis

from investapi.models import CryptoResponse
from investapi.utils import handle_error_exception, CRYPTO_SYMBOLS


async def get_crypto_price(coin: str, redis_client: redis.Redis | None):
    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()
    cache_key = f"coin:{coin}"

    cached = None
    if redis_client is not None:
        try:
            cached = await redis_client.get(cache_key)
        except Exception as e:
            pass

    if cached:
        return CryptoResponse(**json.loads(cached))

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            price = data.get(coin, {}).get("usd")
            if price is None:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Not Found", "detail": f"Cryptocurrency {coin} not found"}
                )

            response_data = CryptoResponse(name=coin, price=round(price, 2), currency="USD", source="CoinGecko", cached_at=datetime.now()) # type: ignore

            if redis_client is not None:
                try:
                    await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
                except Exception as e:
                    pass

            return response_data
    except Exception as e:
        raise handle_error_exception(e, source="CoinGecko API")