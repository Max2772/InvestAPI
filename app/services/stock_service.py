from datetime import datetime
from typing import Union

import yfinance as yf
from fastapi.responses import JSONResponse

from app.config import logger
from app.database import RedisClient
from app.schemas import StockResponse
from app.services.error_handler import handle_error_exception


async def get_stock_price(
    ticker: str,
    redis_client: RedisClient | None,
) -> Union[StockResponse, JSONResponse]:
    ticker = ticker.upper()
    cache_key = f"stock:{ticker}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key)
        if cache:
            return cache

    try:
        logger.info(f"Fetching stock data for {ticker} from Yahoo Finance")
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        if not info or "symbol" not in info:
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": f"Stock {ticker} not found"},
            )

        stock_price = yf_ticker.fast_info.last_price
        company_name = info.get("shortName")
        if not stock_price or not company_name:
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": f"Stock {ticker} not found"},
            )

        response_data = StockResponse(
            name=ticker,
            full_name=company_name,
            price=round(stock_price, 2),
            currency="USD",
            source="Yahoo Finance",
            cached_at=datetime.now(),
        )

        if redis_client:
            await redis_client.set_cache(cache_key, response_data)

        return response_data
    except Exception as e:
        logger.error(f"Error fetching stock {ticker}: {e}")
        raise handle_error_exception(e, source="Yahoo Finance API") from e
