from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas import (
    CryptoResponse,
    StockResponse,
    SteamResponse,
    CryptoHistoryResponse,
    StockHistoryResponse,
    SteamHistoryResponse,
    HistoryPoint,
)

FIXED_TIME = datetime(2026, 5, 22, 12, 0, 0)


@pytest.fixture
def fake_http_session():
    def factory(response: FakeAiohttpResponse) -> FakeAiohttpSession:
        return FakeAiohttpSession(response)

    return factory


@pytest_asyncio.fixture
async def client(fake_http_session):
    app.state.redis_client = None
    app.state.http_session = fake_http_session(FakeAiohttpResponse({}))
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def sample_stock() -> StockResponse:
    return StockResponse(
        name="AMD",
        full_name="Advanced Micro Devices, Inc.",
        price=150.25,
        currency="USD",
        source="Yahoo Finance",
        cached_at=FIXED_TIME,
    )


@pytest.fixture
def sample_crypto() -> CryptoResponse:
    return CryptoResponse(
        name="solana",
        symbol="SOL",
        full_name="Solana",
        price=145.5,
        currency="USD",
        source="CoinGecko",
        cached_at=FIXED_TIME,
    )


@pytest.fixture
def sample_stock_history() -> StockHistoryResponse:
    return StockHistoryResponse(
        name="AMD",
        full_name="Advanced Micro Devices, Inc.",
        interval="1d",
        points=[
            HistoryPoint(
                timestamp=FIXED_TIME,
                price=150.25,
                volume=1_000_000.0,
            )
        ],
        cached_at=FIXED_TIME,
    )


@pytest.fixture
def sample_crypto_history() -> CryptoHistoryResponse:
    return CryptoHistoryResponse(
        name="solana",
        symbol="SOL",
        full_name="Solana",
        points=[HistoryPoint(timestamp=FIXED_TIME, price=145.5, volume=1_000_000.0)],
        cached_at=FIXED_TIME,
    )


@pytest.fixture
def sample_steam_history() -> SteamHistoryResponse:
    return SteamHistoryResponse(
        app_id=730,
        name="Glove Case",
        points=[HistoryPoint(timestamp=FIXED_TIME, price=14.97, volume=42.0)],
        cached_at=FIXED_TIME,
    )


@pytest.fixture
def sample_steam() -> SteamResponse:
    return SteamResponse(
        app_id=730,
        name="Glove Case",
        price=14.97,
        currency="USD",
        source="Steam Market",
        cached_at=FIXED_TIME,
    )


class FakeAiohttpResponse:
    def __init__(self, payload: Any, *, raise_for_status: Exception | None = None):
        self._payload = payload
        self._raise_for_status = raise_for_status

    async def json(self) -> Any:
        return self._payload

    async def text(self) -> str:
        if isinstance(self._payload, str):
            return self._payload
        raise TypeError("FakeAiohttpResponse.text() requires a string payload")

    def raise_for_status(self) -> None:
        if self._raise_for_status is not None:
            raise self._raise_for_status


class FakeAiohttpGetCtx:
    def __init__(self, response: FakeAiohttpResponse):
        self._response = response

    async def __aenter__(self) -> FakeAiohttpResponse:
        return self._response

    async def __aexit__(self, *args: object) -> None:
        return None


class FakeAiohttpSession:
    def __init__(self, response: FakeAiohttpResponse):
        self._response = response

    def get(self, url: str, **_kwargs: object) -> FakeAiohttpGetCtx:
        return FakeAiohttpGetCtx(self._response)

    async def __aenter__(self) -> "FakeAiohttpSession":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None


class FakeRedisBackend:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value

    async def close(self) -> None:
        return None


@pytest.fixture
def fake_redis_backend() -> FakeRedisBackend:
    return FakeRedisBackend()


@pytest.fixture
def redis_client(fake_redis_backend: FakeRedisBackend):
    from app.database import RedisClient

    client = RedisClient()
    client._client = fake_redis_backend
    return client


@pytest.fixture
def mock_yfinance_ticker(monkeypatch: pytest.MonkeyPatch):
    def configure(info: dict | None, last_price: float | None) -> None:
        def ticker_factory(_symbol: str) -> MagicMock:
            ticker = MagicMock()
            ticker.info = info
            ticker.fast_info = MagicMock(last_price=last_price)
            return ticker

        monkeypatch.setattr("app.services.stock_price.yf.Ticker", ticker_factory)

    return configure


@pytest.fixture
def mock_yfinance_history(monkeypatch: pytest.MonkeyPatch):
    def configure(
        history_df,
        info: dict | None = None,
        *,
        on_call: object | None = None,
    ) -> None:
        def ticker_factory(_symbol: str) -> MagicMock:
            if on_call is not None:
                on_call()
            ticker = MagicMock()
            ticker.history.return_value = history_df
            ticker.info = info or {}
            return ticker

        monkeypatch.setattr("app.services.stock_history.yf.Ticker", ticker_factory)

    return configure
