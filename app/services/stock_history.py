import asyncio
from datetime import datetime

import pandas as pd
import yfinance as yf

from app.config import REDIS_STOCK_HISTORY_INTERVAL, STOCK_HISTORY_YFINANCE_PERIOD
from app.database import RedisClient
from app.schemas.history_responses import HistoryPoint, StockHistoryResponse
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.history_points import DAILY_INTERVAL, filter_points_by_days
from app.utils.logging import logger


def _cache_key(ticker: str) -> str:
    return f"stock:history:{ticker}"


def _fetch_history(ticker: str) -> tuple[pd.DataFrame, str | None]:
    yf_ticker = yf.Ticker(ticker)
    df = yf_ticker.history(period=STOCK_HISTORY_YFINANCE_PERIOD, interval=DAILY_INTERVAL)
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


def _slice_cached(cached: StockHistoryResponse, ticker: str, days: int) -> StockHistoryResponse:
    points = filter_points_by_days(cached.points, days)
    if not points:
        raise AssetNotFoundError(f"Stock history for {ticker} not found")
    return StockHistoryResponse(
        name=ticker,
        full_name=cached.full_name,
        interval=DAILY_INTERVAL,
        points=points,
        cached_at=cached.cached_at,
    )


async def get_stock_history(
    ticker: str,
    days: int,
    redis_client: RedisClient | None,
) -> StockHistoryResponse:
    ticker = ticker.upper()
    cache_key = _cache_key(ticker)

    if redis_client:
        cached = await redis_client.get_model_cache(cache_key, StockHistoryResponse)
        if cached and cached.points:
            return _slice_cached(cached, ticker, days)

    try:
        logger.info(
            f"Fetching stock history for {ticker} "
            f"(period={STOCK_HISTORY_YFINANCE_PERIOD}, interval={DAILY_INTERVAL})"
        )
        df, full_name = await asyncio.to_thread(_fetch_history, ticker)
        if df.empty:
            raise AssetNotFoundError(f"Stock history for {ticker} not found")

        points = _dataframe_to_points(df)
        if not points:
            raise AssetNotFoundError(f"Stock history for {ticker} not found")

        cached_at = datetime.now()
        full_response = StockHistoryResponse(
            name=ticker,
            full_name=full_name,
            interval=DAILY_INTERVAL,
            points=points,
            cached_at=cached_at,
        )

        if redis_client:
            await redis_client.set_model_cache(
                cache_key, full_response, REDIS_STOCK_HISTORY_INTERVAL
            )

        return _slice_cached(full_response, ticker, days)
    except AssetNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock history for {ticker}: {e}")
        raise handle_error_exception(e, source="Yahoo Finance API") from e
