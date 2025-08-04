import json
import yfinance as yf
from datetime import datetime
from fastapi import HTTPException
from models.price_response import StockResponse
from utils import handle_error_exception, redis_client

async def get_stock_price(ticker: str):

    cache_key = f"stock:{ticker}"
    cached = redis_client.get(cache_key)

    if cached:
        return StockResponse(**json.loads(cached))

    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        if history.empty:
            raise HTTPException(status_code=404, detail="Stock not found")

        price = history["Close"].iloc[-1]
        response_data = StockResponse(name=ticker, price=round(price, 2), currency="USD", source="Yahoo Finance", cached_at=datetime.now())
        redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(mode="json")))
        return response_data
    except Exception as e:
        raise handle_error_exception(e, source="Yahoo Finance API")