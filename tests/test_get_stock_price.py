import json
from datetime import datetime

import pytest
import fakeredis
from unittest.mock import Mock

from src.services.stock_service import get_stock_price
from src.models.price_response import StockResponse


@pytest.fixture()
def fake_redis():
    return fakeredis.aioredis.FakeRedis()

@pytest.mark.asyncio
async def test_get_stock_price(mocker, fake_redis):
    mocker.patch("src.utils.redis_client.get_redis", return_value=fake_redis)

    FakeStockResponse = StockResponse(
        name='AAPL',
        price=123.45,
        currency='USD',
        source='Yahoo Finance',
        cached_at=datetime.now()
    )

    mock_ticker = Mock()
    mock_ticker.info = {'symbol': 'AAPL'}
    mock_ticker.fast_info.last_price = 123.45

    mocker.patch("src.services.stock_service.yf.Ticker", return_value=mock_ticker)

    # Not Cache
    result1 = await get_stock_price(FakeStockResponse.name)
    assert result1.model_dump(exclude={"cached_at"}) == FakeStockResponse.model_dump(exclude={"cached_at"})
    assert isinstance(result1.cached_at, datetime)
    assert isinstance(result1, StockResponse)

    cached = await fake_redis.set('stock:AAPL', json.dumps(FakeStockResponse.model_dump(mode="json")))
    assert cached is True

    # Cached Redis
    result2 = await get_stock_price(FakeStockResponse.name)
    assert result2.model_dump(exclude={"cached_at"}) == FakeStockResponse.model_dump(exclude={"cached_at"})
    assert isinstance(result2.cached_at, datetime)
    assert isinstance(result2, StockResponse)