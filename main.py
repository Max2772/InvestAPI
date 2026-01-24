from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.dependencies import redisDep
from src.env import LOG_LEVEL, API_HOST, API_PORT, API_RELOAD
from src.logger import logger
from src.models import StockResponse, CryptoResponse, SteamResponse
from src.services import get_stock_price, get_crypto_price, get_steam_item_price
from src.utils.redis_client import RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.redis_client = RedisClient()
        if await app.state.redis_client.test_connection():
            logger.info("Redis connection established successfully.")
        else:
            logger.warning("Redis connection failed. Falling back to no-cache mode.")
            app.state.redis_client = None
    except Exception as e:
        logger.error(f"Critical error during Redis startup: {e}")
        app.state.redis_client = None

    yield

    if app.state.redis_client:
        try:
            await app.state.redis_client.client.close()
            logger.info("Redis connection closed.")
        except Exception as e:
            logger.warning(f"Error closing Redis: {e}")


app = FastAPI(
    title='InvestAPI',
    description="API for fetching real-time prices of stocks, cryptocurrencies, and Steam assets",
    version='1.1.0',
    lifespan=lifespan
)


@app.get('/', tags=['Index'])
async def index():
    return {'Nothing here, look docs'}


@app.get("/stock/{ticker}", response_model=StockResponse, tags=['Stocks'], summary="Get stock price")
async def stock_price(ticker: str, redis_client: redisDep):
    return await get_stock_price(ticker, redis_client)


@app.get("/crypto/{coin}", response_model=CryptoResponse, tags=['Crypto'], summary="Get crypto price")
async def crypto_price(coin: str, redis_client: redisDep):
    return await get_crypto_price(coin, redis_client)


@app.get("/steam/{app_id}/{market_hash_name}", response_model=SteamResponse, tags=['Steam'], summary="Get steam item price")
async def steam_price(app_id: int, market_hash_name: str, redis_client: redisDep):
    return await get_steam_item_price(app_id, market_hash_name, redis_client)


if __name__ == '__main__':
    logger.info("Staring FastAPI server...")

    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level=LOG_LEVEL.lower(),
        access_log=True
    )