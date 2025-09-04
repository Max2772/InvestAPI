from typing import Union
import json
from datetime import datetime
from urllib import quote

import aiohttp
from fastapi.responses import JSONResponse

from src.models.price_response import SteamResponse
from src.utils import handle_error_exception, get_redis


async def get_steam_item_price(app_id: int, market_hash_name: str) -> Union[SteamResponse, JSONResponse]:
    cache_key = f"steam:{app_id}:{market_hash_name}"

    redis_client = await get_redis()
    if redis_client:
        cache = await redis_client.get(cache_key)
        if cache:
            return SteamResponse(**json.loads(cache))

    try:
        url = f"https://steamcommunity.com/market/priceoverview/?appid={app_id}&market_hash_name={quote(market_hash_name)}&currency=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
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
    response_data = SteamResponse(
        app_id=app_id,
        market_name=market_hash_name,
        price=clean_price,
        currency="USD",
        source="Steam Market",
        cached_at=datetime.now()
    )

    if redis_client:
        await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))

    return response_data
