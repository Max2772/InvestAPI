import json
from datetime import datetime

import pytest
import fakeredis
from unittest.mock import Mock, AsyncMock

from src.services.crypto_service import get_crypto_price
from src.models.price_response import CryptoResponse


@pytest.fixture()
def fake_redis():
    return fakeredis.aioredis.FakeRedis()

@pytest.mark.asyncio
async def test_get_crypto_price(mocker, fake_redis):
    mocker.patch("src.utils.redis_client.get_redis", return_value=fake_redis)

    fake_crypto_response = CryptoResponse(
        name='BTC',
        price=123456.78,
        currency='USD',
        source='Gecko API',
        cached_at=datetime.now()
    )

    fake_response = AsyncMock()
    fake_response.json = AsyncMock(return_value={"bitcoin": {"usd": 123456}})
    fake_response.raise_for_status = AsyncMock()

    fake_session = AsyncMock()
    fake_session.get.return_value.__aenter__.return_value = fake_response

    fake_session_cm = AsyncMock()  # сам контекстный менеджер для ClientSession
    fake_session_cm.__aenter__.return_value = fake_session

    mocker.patch("src.services.crypto_service.aiohttp.ClientSession", return_value=fake_session_cm)

    # Not Cache
    result1 = await get_crypto_price(fake_crypto_response.name)
    assert result1.model_dump(exclude={"cached_at"}) == fake_crypto_response.model_dump(exclude={"cached_at"})





    # assert isinstance(result1.cached_at, datetime)
    # assert isinstance(result1, CryptoResponse)

    # cached = await fake_redis.set('coin:bitcoin', json.dumps(fake_crypto_response.model_dump(mode="json")))
    # assert cached is True
    #
    # # Cached Redis
    # result2 = await get_crypto_price(fake_crypto_response.name)
    # assert result2.model_dump(exclude={"cached_at"}) == fake_crypto_response.model_dump(exclude={"cached_at"})
    # assert isinstance(result2.cached_at, datetime)
    # assert isinstance(result2, CryptoResponse)