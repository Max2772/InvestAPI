import json
import httpx
from datetime import datetime
from fastapi.responses import JSONResponse

from investapi.models import SteamResponse
from investapi.utils import handle_error_exception, redis_client


async def get_steam_item_price(app_id: int, market_hash_name: str):

    cache_key = f"steam:{app_id}:{market_hash_name}"
    cached = None
    if redis_client is not None:
        try:
            cached = redis_client.get(cache_key)
        except Exception as e:
            pass

    if cached:
        return SteamResponse(**json.loads(cached))

    try:
        url = f"https://steamcommunity.com/market/priceoverview/?appid={app_id}&market_hash_name={market_hash_name}&currency=1"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        raise handle_error_exception(e, source="Steam Market API")
    if not data.get("success"):
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": "success == False"}
        )

    price = data.get("lowest_price")
    if price is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "detail": "Steam item not found"}
        )
    clean_price = float(price.replace("$", ""))

    response_data = SteamResponse(app_id=app_id, item_name=market_hash_name, price=clean_price, currency="USD", source="Steam Market", cached_at=datetime.now())
    if redis_client is not None:
        try:
            redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
        except Exception as e:
            pass

    return response_data
