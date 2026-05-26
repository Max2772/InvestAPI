from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.types.enums.enums import AssetType
from app.utils import AssetNotFoundError
from app.schemas import (
    CryptoPricesResponse,
    StockResponse,
    SteamResponse,
    StockHistoryResponse,
    CryptoHistoryResponse,
    SteamHistoryResponse,
)
from tests.conftest import (
    FIXED_TIME,
    sample_crypto,
    sample_stock,
    sample_steam,
    sample_stock_history,
    sample_crypto_history,
    sample_steam_history,
)


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
async def test_stock_history_endpoint_returns_service_result(
    client, monkeypatch, sample_stock_history
):
    monkeypatch.setattr(
        "app.routers.assets.get_stock_history",
        AsyncMock(return_value=sample_stock_history),
    )

    response = await client.get("/stock/AMD/history?days=90")

    assert response.status_code == 200
    history = StockHistoryResponse.model_validate(response.json())
    assert history.name == "AMD"
    assert len(history.points) == 1
    assert history.asset_type == AssetType.STOCK


@pytest.mark.asyncio
async def test_crypto_history_endpoint_returns_service_result(
    client, monkeypatch, sample_crypto_history
):
    monkeypatch.setattr(
        "app.routers.assets.get_crypto_history",
        AsyncMock(return_value=sample_crypto_history),
    )

    response = await client.get("/crypto/solana/history?days=30")

    assert response.status_code == 200
    history = CryptoHistoryResponse.model_validate(response.json())
    assert history.name == "solana"
    assert history.asset_type == AssetType.CRYPTO


@pytest.mark.asyncio
async def test_crypto_endpoint_returns_service_result(client, monkeypatch, sample_crypto):
    from app.schemas import CryptoPricesResponse

    monkeypatch.setattr(
        "app.routers.assets.get_crypto_prices",
        AsyncMock(return_value=CryptoPricesResponse(coins=[sample_crypto])),
    )

    response = await client.get("/crypto/solana")

    assert response.status_code == 200
    payload = CryptoPricesResponse.model_validate(response.json())
    assert len(payload.coins) == 1
    assert payload.coins[0].name == "solana"
    assert payload.coins[0].asset_type == AssetType.CRYPTO


@pytest.mark.asyncio
async def test_steam_history_endpoint_returns_service_result(
    client, monkeypatch, sample_steam_history
):
    monkeypatch.setattr(
        "app.routers.assets.get_steam_item_history",
        AsyncMock(return_value=sample_steam_history),
    )

    response = await client.get("/steam/730/Glove%20Case/history?days=90")

    assert response.status_code == 200
    history = SteamHistoryResponse.model_validate(response.json())
    assert history.app_id == 730
    assert history.name == "Glove Case"
    assert history.asset_type == AssetType.STEAM


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
