from typing import Union
import json
from datetime import datetime

import yfinance as yf
from fastapi.responses import JSONResponse

from src.models.price_response import StockResponse
from src.utils import handle_error_exception, get_logger, get_redis


logger = get_logger()

async def get_stock_price(ticker: str) -> Union[StockResponse, JSONResponse]:
    ticker = ticker.upper()
    cache_key = f"stock:{ticker}"

    redis_client = await get_redis()
    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return StockResponse(**json.loads(cached))
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        if not info or 'symbol' not in info:
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": f"Stock {ticker} not found"}
            )

        stock_price = yf_ticker.fast_info.last_price
        if not stock_price:
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": f"Stock {ticker} not found"}
            )

        response_data = StockResponse(
            name=ticker,
            price=round(stock_price, 2),
            currency="USD",
            source="Yahoo Finance",
            cached_at=datetime.now()
        )

        if redis_client:
            print(f"Writing {cache_key} to Redis")
            await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(mode="json")))

        return response_data
    except Exception as e:
        raise handle_error_exception(e, source="Yahoo Finance API")