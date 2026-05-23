import json

import pytest

from app.types.enums.enums import AssetType
from app.schemas import CryptoResponse, StockResponse, SteamResponse
from tests.conftest import FIXED_TIME


@pytest.mark.asyncio
async def test_set_and_get_stock_cache(redis_client, sample_stock: StockResponse):
    await redis_client.set_cache("stock:AMD", sample_stock, ttl=900)
    cached = await redis_client.get_cache("stock:AMD", StockResponse)

    assert cached is not None
    assert isinstance(cached, StockResponse)
    assert cached.name == "AMD"
    assert cached.price == sample_stock.price


@pytest.mark.asyncio
async def test_get_cache_miss(redis_client):
    assert await redis_client.get_cache("stock:MISSING", StockResponse) is None


@pytest.mark.asyncio
async def test_get_cache_invalid_payload(redis_client):
    redis_client._client.store["bad"] = json.dumps({"name": "broken"})
    assert await redis_client.get_cache("bad", StockResponse) is None


@pytest.mark.asyncio
async def test_get_cache_crypto_and_steam(redis_client):
    crypto = CryptoResponse(
        name="bitcoin",
        price=1.0,
        currency="USD",
        source="CoinGecko",
        cached_at=FIXED_TIME,
    )
    steam = SteamResponse(
        app_id=730,
        name="Case",
        price=2.0,
        currency="USD",
        source="Steam Market",
        cached_at=FIXED_TIME,
    )

    await redis_client.set_cache("coin:bitcoin", crypto, ttl=300)
    await redis_client.set_cache("steam:730:Case", steam, ttl=900)

    assert (await redis_client.get_cache("coin:bitcoin", CryptoResponse)).asset_type == AssetType.CRYPTO
    assert (await redis_client.get_cache("steam:730:Case", SteamResponse)).app_id == 730


@pytest.mark.asyncio
async def test_test_connection_success(redis_client):
    assert await redis_client.test_connection() is True


@pytest.mark.asyncio
async def test_test_connection_ping_false(monkeypatch):
    from app.database import RedisClient

    backend = type("B", (), {"ping": lambda self: False})()
    client = RedisClient()
    client._client = backend  # type: ignore[assignment]
    assert await client.test_connection() is False
