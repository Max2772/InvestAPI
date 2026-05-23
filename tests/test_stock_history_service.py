import pandas as pd
import pytest
from fastapi import HTTPException

from app.schemas.history_responses import StockHistoryResponse
from app.services.stock_history import get_stock_history
from app.utils import AssetNotFoundError
from tests.conftest import FIXED_TIME, sample_stock_history


@pytest.mark.asyncio
async def test_stock_history_success(mock_yfinance_history):
    df = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [110.0],
            "Low": [95.0],
            "Close": [105.5],
            "Volume": [1000.0],
        },
        index=[pd.Timestamp("2026-05-01")],
    )
    mock_yfinance_history(df, {"shortName": "Advanced Micro Devices, Inc."})

    result = await get_stock_history("amd", "1mo", "1d", None)

    assert isinstance(result, StockHistoryResponse)
    assert result.name == "AMD"
    assert result.full_name == "Advanced Micro Devices, Inc."
    assert len(result.points) == 1
    assert result.points[0].price == 105.5
    assert result.points[0].volume == 1000.0


@pytest.mark.asyncio
async def test_stock_history_not_found_empty(mock_yfinance_history):
    mock_yfinance_history(pd.DataFrame())

    with pytest.raises(AssetNotFoundError, match="Stock history for FAKE not found"):
        await get_stock_history("FAKE", "1mo", "1d", None)


@pytest.mark.asyncio
async def test_stock_history_cache_hit(
    redis_client, sample_stock_history, mock_yfinance_history
):
    def fail_if_yfinance_called() -> None:
        pytest.fail("yfinance must not be called on cache hit")

    mock_yfinance_history(pd.DataFrame(), on_call=fail_if_yfinance_called)
    await redis_client.set_model_cache(
        "stock:history:AMD:3mo:1d",
        sample_stock_history,
        ttl=3600,
    )

    result = await get_stock_history("AMD", "3mo", "1d", redis_client)

    assert result == sample_stock_history


@pytest.mark.asyncio
async def test_stock_history_unexpected_error(monkeypatch):
    def raise_error(_ticker: str) -> None:
        raise RuntimeError("yahoo down")

    monkeypatch.setattr("app.services.stock_history_service.yf.Ticker", raise_error)

    with pytest.raises(HTTPException) as exc_info:
        await get_stock_history("AMD", "1mo", "1d", None)

    assert exc_info.value.status_code == 500
