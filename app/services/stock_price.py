from datetime import datetime

import yfinance as yf

from app.config import REDIS_STOCK_INTERVAL, STOCK_PROVIDER_NAME
from app.database import RedisClient
from app.schemas import StockResponse
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.logging import logger


def _fetch_stock_price(ticker: str) -> StockResponse:
    logger.info(f"Fetching stock data for {ticker} from {STOCK_PROVIDER_NAME}")
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info
    if not info or "symbol" not in info:
        raise AssetNotFoundError(f"Stock {ticker} not found")

    stock_price = yf_ticker.fast_info.last_price
    company_name = info.get("shortName")
    if not stock_price or not company_name:
        raise AssetNotFoundError(f"Stock {ticker} not found")

    return StockResponse(
        name=ticker,
        full_name=company_name,
        price=round(stock_price, 2),
        currency="USD",
        cached_at=datetime.now(),
    )


async def get_stock_price(
    ticker: str,
    redis_client: RedisClient | None,
) -> StockResponse:
    ticker = ticker.upper()
    cache_key = f"stock:{ticker}"

    if redis_client:
        cache = await redis_client.get_cache(cache_key, StockResponse)
        if cache:
            return cache

    try:
        response_data = _fetch_stock_price(ticker)

        if redis_client:
            await redis_client.set_cache(cache_key, response_data, REDIS_STOCK_INTERVAL)

        return response_data
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock {ticker}: {e}")
        raise handle_error_exception(e, source=STOCK_PROVIDER_NAME) from e