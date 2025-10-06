import argparse

import uvicorn
from fastapi import FastAPI

from src.utils import setup_logger, init_redis
from src.models import StockResponse, CryptoResponse, SteamResponse
from src.services import get_stock_price, get_crypto_price, get_steam_item_price


app = FastAPI(
    title='Investment API',
    description="API for fetching real-time prices of stocks, cryptocurrencies, and Steam items",
    version='1.0.0'
)

@app.on_event("startup")
async def startup_event():
    await init_redis()


@app.get('/', tags=['Index'])
async def index():
    return {'Nothing here, look docs'}


@app.get("/stock/{ticker}", response_model=StockResponse, tags=['Stocks'], summary="Get stock price")
async def stock_price(ticker: str):
    return await get_stock_price(ticker)


@app.get("/crypto/{coin}", response_model=CryptoResponse, tags=['Crypto'], summary="Get crypto price")
async def crypto_price(coin: str):
    return await get_crypto_price(coin)


@app.get("/steam/{app_id}/{market_hash_name}", response_model=SteamResponse, tags=['Steam'], summary="Get steam item price")
async def steam_price(app_id: int, market_hash_name: str):
    return await get_steam_item_price(app_id, market_hash_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", type=str, default=None,
                        help="Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    args = parser.parse_args()

    if args.log_level:
        log_level = args.log_level.upper()
        logger = setup_logger(log_level)
    else:
        logger = setup_logger()

    logger.info('FastAPI Started')

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')