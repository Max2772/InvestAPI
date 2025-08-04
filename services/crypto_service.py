import json
import httpx
from datetime import datetime
from fastapi import HTTPException
from models.price_response import CryptoResponse
from utils import handle_error_exception, redis_client, CRYPTO_SYMBOLS

async def get_crypto_price(coin: str):

    coin = CRYPTO_SYMBOLS.get(coin.upper(), coin).lower()

    cache_key = f"coin:{coin}"
    cached = redis_client.get(cache_key)

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
                raise HTTPException(status_code=404, detail="Cryptocurrency not found")

            response_data = CryptoResponse(name=coin, price=round(price, 2), currency="USD", source="CoinGecko", cached_at=datetime.now())
            redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
            return response_data
    except Exception as e:
        raise handle_error_exception(e, source="CoinGecko API")