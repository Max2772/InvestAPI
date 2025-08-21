import json
import aiohttp
from datetime import datetime
from fastapi.responses import JSONResponse

from src.models.price_response import SteamResponse
from src.utils import handle_error_exception, redis_client, get_logger


logger = get_logger()


async def get_steam_item_price(app_id: int, market_hash_name: str):
    logger.info(f"Requesting price for Steam item: app_id={app_id}, market_hash_name={market_hash_name}")

    cache_key = f"steam:{app_id}:{market_hash_name}"
    cache = None

    if redis_client is not None:
        cache = await redis_client.get(cache_key)

    if cache:
        logger.info(f"Found cached data for steam:{app_id}:{market_hash_name} in Redis")
        return SteamResponse(**json.loads(cache))

    try:
        url = f"https://steamcommunity.com/market/priceoverview/?appid={app_id}&market_hash_name={market_hash_name}&currency=1"
        logger.info(f"Sending request to Steam Market API: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
    except Exception as e:
        logger.error(f"Error fetching data from Steam Market API for app_id={app_id}, market_hash_name={market_hash_name}: {str(e)}")
        raise handle_error_exception(e, source="Steam Market API")
    if not data.get("success"):
        logger.warning(f"Steam Market API returned success=False for app_id={app_id}, market_hash_name={market_hash_name}")
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": "success == False"}
        )

    price = data.get("lowest_price")
    if price is None:
        logger.warning(f"Price not found for app_id={app_id}, market_hash_name={market_hash_name}")
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "detail": "Steam item not found"}
        )

    clean_price = float(price.replace("$", ""))
    response_data = SteamResponse(
        app_id=app_id,
        item_name=market_hash_name,
        price=clean_price,
        currency="USD",
        source="Steam Market",
        cached_at=datetime.now()
    )

    if redis_client is not None:
        await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
        logger.info(f"Cached data for steam:{app_id}:{market_hash_name} for 900 seconds")

    logger.info(f"Price for app_id={app_id}, market_hash_name={market_hash_name} retrieved: ${clean_price:.2f}")
    return response_data
