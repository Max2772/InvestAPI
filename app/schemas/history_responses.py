from datetime import datetime

from pydantic import BaseModel, Field

from app.types.enums.enums import AssetType


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
    source: str = "Yahoo Finance API"
    cached_at: datetime


class CryptoHistoryResponse(BaseModel):
    asset_type: AssetType = AssetType.CRYPTO
    name: str
    interval: str = "1d"
    points: list[HistoryPoint] = Field(default_factory=list)
    source: str = "CoinGecko API"
    cached_at: datetime


class SteamHistoryResponse(BaseModel):
    asset_type: AssetType = AssetType.STEAM
    app_id: int
    name: str
    interval: str = "1d"
    points: list[HistoryPoint] = Field(default_factory=list)
    source: str = "Steam Market"
    cached_at: datetime
