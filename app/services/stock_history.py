import asyncio
from datetime import datetime

import pandas as pd
import yfinance as yf

from app.config import REDIS_STOCK_HISTORY_INTERVAL
from app.database import RedisClient
from app.schemas.history_responses import HistoryPoint, StockHistoryResponse
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.logging import logger


def _fetch_history(
    ticker: str, period: str, interval: str
) -> tuple[pd.DataFrame, str | None]:
    yf_ticker = yf.Ticker(ticker)
    df = yf_ticker.history(period=period, interval=interval)
    full_name: str | None = None
    try:
        info = yf_ticker.info
        if info:
            full_name = info.get("shortName")
    except Exception:
        pass
    return df, full_name


def _dataframe_to_points(df: pd.DataFrame) -> list[HistoryPoint]:
    points: list[HistoryPoint] = []
    for index, row in df.iterrows():
        close = row.get("Close")
        if close is None or pd.isna(close):
            continue

        ts = index.to_pydatetime() if hasattr(index, "to_pydatetime") else index
        if getattr(ts, "tzinfo", None) is not None:
            ts = ts.replace(tzinfo=None)

        volume = row.get("Volume")
        volume_value: float | None = None
        if volume is not None and not pd.isna(volume):
            volume_value = round(float(volume), 4)

        points.append(
            HistoryPoint(
                timestamp=ts,
                price=round(float(close), 4),
                volume=volume_value,
            )
        )
    return points


async def get_stock_history(
    ticker: str,
    period: str,
    interval: str,
    redis_client: RedisClient | None,
) -> StockHistoryResponse:
    ticker = ticker.upper()
    cache_key = f"stock:history:{ticker}:{period}:{interval}"

    if redis_client:
        cache = await redis_client.get_model_cache(cache_key, StockHistoryResponse)
        if cache:
            return cache

    try:
        logger.info(
            f"Fetching stock history for {ticker} (period={period}, interval={interval})"
        )
        df, full_name = await asyncio.to_thread(_fetch_history, ticker, period, interval)
        if df.empty:
            raise AssetNotFoundError(f"Stock history for {ticker} not found")

        points = _dataframe_to_points(df)
        if not points:
            raise AssetNotFoundError(f"Stock history for {ticker} not found")

        response_data = StockHistoryResponse(
            name=ticker,
            full_name=full_name,
            interval=interval,
            points=points,
            cached_at=datetime.now(),
        )

        if redis_client:
            await redis_client.set_model_cache(
                cache_key, response_data, REDIS_STOCK_HISTORY_INTERVAL
            )

        return response_data
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock history for {ticker}: {e}")
        raise handle_error_exception(e, source=StockHistoryResponse.source) from e
