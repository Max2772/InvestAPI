import pytest
from fastapi import HTTPException

from app.schemas import CryptoResponse
from app.services.crypto_price import get_crypto_prices
from app.utils import AssetNotFoundError
from tests.conftest import FakeAiohttpResponse, sample_crypto


@pytest.mark.asyncio
async def test_crypto_success(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": 145.567}}))

    result = await get_crypto_prices("solana", None, session)

    assert len(result.coins) == 1
    coin = result.coins[0]
    assert isinstance(coin, CryptoResponse)
    assert coin.name == "solana"
    assert coin.symbol == "SOL"
    assert coin.full_name == "Solana"
    assert coin.price == 145.57


@pytest.mark.asyncio
async def test_crypto_symbol_alias(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": 10.0}}))

    result = await get_crypto_prices("SOL", None, session)

    assert len(result.coins) == 1
    assert result.coins[0].name == "solana"
    assert result.coins[0].symbol == "SOL"
    assert result.coins[0].full_name == "Solana"


@pytest.mark.asyncio
async def test_crypto_batch_single_http_request(fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse(
            {
                "bitcoin": {"usd": 75000.0},
                "ethereum": {"usd": 2000.0},
            }
        )
    )

    result = await get_crypto_prices("bitcoin,ethereum", None, session)

    assert len(result.coins) == 2
    assert result.coins[0].name == "bitcoin"
    assert result.coins[1].name == "ethereum"


@pytest.mark.asyncio
async def test_crypto_batch_deduplicates_aliases(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": 80.0}}))

    result = await get_crypto_prices("solana,SOL,Solana", None, session)

    assert len(result.coins) == 1
    assert result.coins[0].name == "solana"


@pytest.mark.asyncio
async def test_crypto_not_found(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({}))

    with pytest.raises(AssetNotFoundError, match="unknowncoin"):
        await get_crypto_prices("unknowncoin", None, session)


@pytest.mark.asyncio
async def test_crypto_invalid_price(fake_http_session):
    session = fake_http_session(FakeAiohttpResponse({"solana": {"usd": "n/a"}}))

    with pytest.raises(
        AssetNotFoundError,
        match="Price not available for cryptocurrencies: solana",
    ):
        await get_crypto_prices("solana", None, session)


@pytest.mark.asyncio
async def test_crypto_cache_hit(redis_client, sample_crypto, fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=AssertionError("HTTP must not be called"))
    )
    await redis_client.set_cache("coin:solana", sample_crypto, ttl=300)

    result = await get_crypto_prices("solana", redis_client, session)

    assert len(result.coins) == 1
    assert result.coins[0] == sample_crypto


@pytest.mark.asyncio
async def test_crypto_partial_cache_hit(redis_client, sample_crypto, fake_http_session):
    session = fake_http_session(
        FakeAiohttpResponse({"ethereum": {"usd": 2000.0}})
    )
    await redis_client.set_cache("coin:solana", sample_crypto, ttl=300)

    result = await get_crypto_prices("solana,ethereum", redis_client, session)

    assert len(result.coins) == 2
    assert result.coins[0] == sample_crypto
    assert result.coins[1].name == "ethereum"
    assert result.coins[1].price == 2000.0


@pytest.mark.asyncio
async def test_crypto_http_error(fake_http_session):
    import aiohttp

    session = fake_http_session(
        FakeAiohttpResponse({}, raise_for_status=aiohttp.ServerTimeoutError("timeout"))
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_crypto_prices("solana", None, session)

    assert exc_info.value.status_code == 504
