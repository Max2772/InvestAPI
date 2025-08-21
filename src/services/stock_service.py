import json
import yfinance as yf
from datetime import datetime
from fastapi.responses import JSONResponse

from src.models.price_response import StockResponse
from src.utils import handle_error_exception, redis_client, get_logger


logger = get_logger()


async def get_stock_price(ticker: str):
    logger.info(f"Requesting price for stock: {ticker}")

    cache_key = f"stock:{ticker}"
    cached = None

    if redis_client is not None:
        cached = await redis_client.get(cache_key)

    if cached:
        logger.info(f"Found cached data for stock:{ticker} in Redis")
        return StockResponse(**json.loads(cached))

    try:
        logger.info(f"Sending request to Yahoo Finance API for {ticker}")
        stock_price = yf.Ticker(ticker).fast_info.last_price
        if not stock_price:
            logger.warning(f"Price not found for {ticker} in Yahoo Finance")
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

        if redis_client is not None:
            await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(mode="json")))
            logger.info(f"Cached data for stock:{ticker} for 900 seconds")

        logger.info(f"Price for {ticker} retrieved: ${stock_price:.2f}")
        return response_data
    except Exception as e:
        logger.error(f"Error fetching data from Yahoo Finance API for {ticker}: {str(e)}")
        raise handle_error_exception(e, source="Yahoo Finance API")