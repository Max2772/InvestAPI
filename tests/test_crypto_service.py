import pytest
from fastapi import HTTPException

from app.schemas import CryptoResponse
from app.services.crypto_price import get_crypto_price
from app.utils import AssetNotFoundError
from tests.conftest import FakeAiohttpResponse, sample_crypto


@pytest.mark.asyncio
async def test_crypto_success(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": 145.567}}))

    result = await get_crypto_price("solana", None, session)

    assert isinstance(result, CryptoResponse)
    assert result.name == "solana"
    assert result.symbol == "SOL"
    assert result.full_name == "Solana"
    assert result.price == 145.57


@pytest.mark.asyncio
async def test_crypto_symbol_alias(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": 10.0}}))

    result = await get_crypto_price("SOL", None, session)

    assert isinstance(result, CryptoResponse)
    assert result.name == "solana"
    assert result.symbol == "SOL"
    assert result.full_name == "Solana"


@pytest.mark.asyncio
async def test_crypto_not_found(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({}))

    with pytest.raises(AssetNotFoundError, match="Cryptocurrency unknowncoin not found"):
        await get_crypto_price("unknowncoin", None, session)


@pytest.mark.asyncio
async def test_crypto_invalid_price(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": "n/a"}}))

    with pytest.raises(
        AssetNotFoundError, match="Price for cryptocurrency solana not available"
    ):
        await get_crypto_price("solana", None, session)


@pytest.mark.asyncio
async def test_crypto_cache_hit(redis_client, sample_crypto, fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=AssertionError("HTTP must not be called"))
    )
    await redis_client.set_cache("coin:solana", sample_crypto, ttl=300)

    result = await get_crypto_price("solana", redis_client, session)

    assert result == sample_crypto


@pytest.mark.asyncio
async def test_crypto_http_error(fake_http_session):
    import aiohttp

    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=aiohttp.ServerTimeoutError("timeout"))
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_crypto_price("solana", None, session)

    assert exc_info.value.status_code == 504
