import json
import aiohttp
from datetime import datetime
from fastapi.responses import JSONResponse

from src.models.price_response import CryptoResponse
from src.utils import handle_error_exception, get_redis, CRYPTO_SYMBOLS


async def get_crypto_price(coin: str):
    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()
    cache_key = f"coin:{coin}"

    _redis_client = await get_redis()
    if _redis_client:
        cached = await _redis_client.get(cache_key)
        if cached:
            return CryptoResponse(**json.loads(cached))

    try:
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

                if _redis_client:
                    await _redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))

                return response_data
    except Exception as e:
        raise handle_error_exception(e, source="CoinGecko API")