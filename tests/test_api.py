from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app
from src.models.asset_responses import StockResponse, CryptoResponse, SteamResponse
from src.types import AssetType

@pytest_asyncio.fixture
async def client():
    app.state.redis_client = None

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_index(client):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == ['Nothing here, look docs']

@pytest.mark.asyncio
async def test_stock(client):
    response = await client.get('/stock/AMD')
    assert response.status_code == 200

    stock: StockResponse = StockResponse.model_validate(response.json())
    assert stock.asset_type == AssetType.STOCK
    assert isinstance(stock.price, float) and stock.price > 0
    assert isinstance(stock.currency, str)
    assert isinstance(stock.source, str)
    assert isinstance(stock.cached_at, datetime)
    assert isinstance(stock.full_name, str)
    assert stock.name == 'AMD'

@pytest.mark.asyncio
async def test_crypto(client):
    response = await client.get('/crypto/solana')
    assert response.status_code == 200

    crypto: CryptoResponse = CryptoResponse.model_validate(response.json())
    assert crypto.asset_type == AssetType.CRYPTO
    assert isinstance(crypto.price, float) and crypto.price > 0
    assert isinstance(crypto.currency, str)
    assert isinstance(crypto.source, str)
    assert isinstance(crypto.cached_at, datetime)
    assert crypto.name == 'solana'

@pytest.mark.asyncio
async def test_steam(client):
    response = await client.get('/steam/730/Glove Case')
    assert response.status_code == 200

    steam: SteamResponse = SteamResponse.model_validate(response.json())
    assert steam.asset_type == AssetType.STEAM
    assert isinstance(steam.price, float) and steam.price > 0
    assert isinstance(steam.currency, str)
    assert isinstance(steam.source, str)
    assert isinstance(steam.cached_at, datetime)
    assert steam.app_id == 730
    assert steam.market_name == 'Glove Case'
