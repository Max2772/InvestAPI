from datetime import datetime
from typing import Union
from urllib.parse import quote

import aiohttp
from fastapi.responses import JSONResponse

from src.logger import logger
from src.models.asset_responses import SteamResponse
from src.utils import handle_error_exception
from src.utils.redis_client import RedisClient


async def get_steam_item_price(
        app_id: int,
        market_hash_name: str,
        redis_client: RedisClient
) -> Union[SteamResponse, JSONResponse]:
    cache_key = f"steam:{app_id}:{market_hash_name}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key)
        if cache:
            return cache

    try:
        logger.info(f"Fetching steam item {market_hash_name}, app_id={app_id} from Steam Market")
        url = f"https://steamcommunity.com/market/priceoverview/?appid={app_id}&market_hash_name={quote(market_hash_name)}&currency=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                response.raise_for_status()

        if not data.get("success"):
            return JSONResponse(
                status_code=502,
                content={"error": "Bad Gateway", "detail": "success == False"}
            )

        price = data.get("lowest_price")
        if price is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": "Steam item price not found"}
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
            await redis_client.set_cache(cache_key, response_data)

        return response_data
    except Exception as e:
        logger.error(f"Error fetching steam item {market_hash_name}, app_id={app_id}: {e}")
        raise handle_error_exception(e, source="Steam Market API")
