from datetime import datetime

from pydantic import BaseModel, Field

from app.config import STOCK_PROVIDER_NAME, CRYPTO_PROVIDER_NAME, STEAM_PROVIDER_NAME
from app.types.enums.enums import AssetType

DAILY_INTERVAL = "1d"


class HistoryPoint(BaseModel):
    timestamp: datetime
    price: float
    volume: float | None = None


class StockHistoryResponse(BaseModel):
    asset_type: AssetType = AssetType.STOCK
    name: str
    full_name: str | None = None
    interval: str
    points: list[HistoryPoint] = Field(default_factory=list)
    source: str = STOCK_PROVIDER_NAME
    cached_at: datetime


class CryptoHistoryResponse(BaseModel):
    asset_type: AssetType = AssetType.CRYPTO
    name: str
    symbol: str
    full_name: str
    interval: str = DAILY_INTERVAL
    points: list[HistoryPoint] = Field(default_factory=list)
    source: str = CRYPTO_PROVIDER_NAME
    cached_at: datetime


class SteamHistoryResponse(BaseModel):
    asset_type: AssetType = AssetType.STEAM
    app_id: int
    name: str
    interval: str = DAILY_INTERVAL
    points: list[HistoryPoint] = Field(default_factory=list)
    source: str = STEAM_PROVIDER_NAME
    cached_at: datetime
