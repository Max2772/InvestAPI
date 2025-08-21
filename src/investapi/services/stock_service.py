import json
import yfinance as yf
from datetime import datetime
from fastapi.responses import JSONResponse

from investapi.models import StockResponse
from investapi.utils import handle_error_exception, redis_client


async def get_stock_price(ticker: str):

    cache_key = f"stock:{ticker}"
    cached = None
    if redis_client is not None:
        try:
            cached = redis_client.get(cache_key)
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

        response_data = StockResponse(name=ticker, price=round(stock_price, 2), currency="USD", source="Yahoo Finance", cached_at=datetime.now())
        if redis_client is not None:
            try:
                redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))
            except Exception as e:
                pass

        return response_data
    except Exception as e:
        raise handle_error_exception(e, source="Yahoo Finance API")