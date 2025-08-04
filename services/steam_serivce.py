import json
import httpx
from datetime import datetime
from fastapi import HTTPException
from models.price_response import SteamResponse
from utils import handle_error_exception, redis_client

async def get_steam_item_price(app_id: int, market_hash_name: str):

    cache_key = f"steam:{app_id}:{market_hash_name}"
    cache = redis_client.get(cache_key)

    if cache:
        return SteamResponse(**json.loads(cache))

    try:
        url = f"https://steamcommunity.com/market/priceoverview/?appid={app_id}&market_hash_name={market_hash_name}&currency=1"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        raise handle_error_exception(e, source="Steam Market API")
    if not data.get("success"):
        raise HTTPException(status_code=404, detail=f"success == False")

    price = data.get("lowest_price")
    if price is None:
        raise HTTPException(status_code=404, detail="Steam item not found")
    clean_price = float(price.replace("$", ""))

    response_data = SteamResponse(app_id=app_id, item_name=market_hash_name, price=clean_price, currency="USD", source="Steam Market", cached_at=datetime.now())
    redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))

    return response_data
