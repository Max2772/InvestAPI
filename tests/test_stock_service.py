import pytest
from fastapi import HTTPException

from app.schemas import StockResponse
from app.services.stock_price import get_stock_price
from app.utils import AssetNotFoundError
from tests.conftest import sample_stock


@pytest.mark.asyncio
async def test_stock_success(mock_yfinance_ticker):
    mock_yfinance_ticker(
        {"symbol": "AMD", "shortName": "Advanced Micro Devices, Inc."},
        150.256,
    )

    result = await get_stock_price("amd", None)

    assert isinstance(result, StockResponse)
    assert result.name == "AMD"
    assert result.price == 150.26


@pytest.mark.asyncio
async def test_stock_not_found_no_symbol(mock_yfinance_ticker):
    mock_yfinance_ticker(None, None)

    with pytest.raises(AssetNotFoundError, match="Stock FAKE not found"):
        await get_stock_price("FAKE", None)


@pytest.mark.asyncio
async def test_stock_not_found_missing_price(mock_yfinance_ticker):
    mock_yfinance_ticker({"symbol": "AMD", "shortName": "AMD"}, None)

    with pytest.raises(AssetNotFoundError, match="Stock AMD not found"):
        await get_stock_price("AMD", None)


@pytest.mark.asyncio
async def test_stock_cache_hit(redis_client, sample_stock, monkeypatch):
    monkeypatch.setattr(
        "app.services.stock_price.yf.Ticker",
        lambda _: pytest.fail("yfinance must not be called on cache hit"),
    )
    await redis_client.set_cache("stock:AMD", sample_stock)

    result = await get_stock_price("AMD", redis_client)

    assert result == sample_stock


@pytest.mark.asyncio
async def test_stock_unexpected_error(monkeypatch):
    def raise_error(_ticker: str) -> None:
        raise RuntimeError("yahoo down")

    monkeypatch.setattr("app.services.stock_price.yf.Ticker", raise_error)

    with pytest.raises(HTTPException) as exc_info:
        await get_stock_price("AMD", None)

    assert exc_info.value.status_code == 500
