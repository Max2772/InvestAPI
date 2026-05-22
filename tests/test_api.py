from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.types.enums.enums import AssetType
from app.utils import AssetNotFoundError
from app.schemas import CryptoResponse, StockResponse, SteamResponse
from tests.conftest import FIXED_TIME, sample_crypto, sample_stock, sample_steam


@pytest.mark.asyncio
async def test_index(client):
    response = await client.get("/", follow_redirects=False)

    assert response.status_code in (301, 302, 307, 308)
    assert response.headers["location"] == "/docs"


@pytest.mark.asyncio
async def test_stock_endpoint_returns_service_result(client, monkeypatch, sample_stock):
    monkeypatch.setattr(
        "app.routers.assets.get_stock_price",
        AsyncMock(return_value=sample_stock),
    )

    response = await client.get("/stock/AMD")

    assert response.status_code == 200
    stock = StockResponse.model_validate(response.json())
    assert stock.name == "AMD"
    assert stock.asset_type == AssetType.STOCK


@pytest.mark.asyncio
async def test_stock_endpoint_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.assets.get_stock_price",
        AsyncMock(side_effect=AssetNotFoundError("Stock FAKE not found")),
    )

    response = await client.get("/stock/FAKE")

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock FAKE not found"


@pytest.mark.asyncio
async def test_crypto_endpoint_returns_service_result(client, monkeypatch, sample_crypto):
    monkeypatch.setattr(
        "app.routers.assets.get_crypto_price",
        AsyncMock(return_value=sample_crypto),
    )

    response = await client.get("/crypto/solana")

    assert response.status_code == 200
    crypto = CryptoResponse.model_validate(response.json())
    assert crypto.name == "solana"
    assert crypto.asset_type == AssetType.CRYPTO


@pytest.mark.asyncio
async def test_steam_endpoint_returns_service_result(client, monkeypatch, sample_steam):
    monkeypatch.setattr(
        "app.routers.assets.get_steam_item_price",
        AsyncMock(return_value=sample_steam),
    )

    response = await client.get("/steam/730/Glove%20Case")

    assert response.status_code == 200
    steam = SteamResponse.model_validate(response.json())
    assert steam.app_id == 730
    assert steam.name == "Glove Case"
    assert isinstance(steam.cached_at, datetime)


@pytest.mark.asyncio
async def test_steam_endpoint_median_only_response(client, monkeypatch):
    steam = SteamResponse(
        app_id=730,
        name="CS20 Case",
        price=2.01,
        currency="USD",
        source="Steam Market",
        cached_at=FIXED_TIME,
    )
    monkeypatch.setattr(
        "app.routers.assets.get_steam_item_price",
        AsyncMock(return_value=steam),
    )

    response = await client.get("/steam/730/CS20%20Case")

    assert response.status_code == 200
    assert response.json()["price"] == 2.01
