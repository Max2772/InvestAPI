import json
import yfinance as yf
from datetime import datetime
from fastapi.responses import JSONResponse
import redis

from investapi.models import StockResponse
from investapi.utils import handle_error_exception


async def get_stock_price(ticker: str, redis_client: redis.Redis | None):
    cache_key = f"stock:{ticker}"
    cached = None
    if redis_client is not None:
        try:
            cached = await redis_client.get(cache_key)
        except Exception as e:
            pass

    if cached:
        return StockResponse(**json.loads(cached))

    try:
        stock_price = yf.Ticker(ticker).fast_info.last_price
        if stock_price is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": f"Stock {ticker} not found"}
            )

        response_data = StockResponse(name=ticker, price=round(float(stock_price), 2), currency="USD", source="Yahoo Finance", cached_at=datetime.now()) # type: ignore
        if redis_client is not None:
            try:
                await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
            except Exception as e:
                pass

        return response_data
    except Exception as e:
        raise handle_error_exception(e, source="Yahoo Finance API")