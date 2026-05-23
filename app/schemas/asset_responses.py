from datetime import datetime

from pydantic import BaseModel

from app.types.enums.enums import AssetType


class BaseAssetResponse(BaseModel):
    price: float
    currency: str = "USD"
    cached_at: datetime


class StockResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.STOCK
    full_name: str
    source: str = "Yahoo Finance API"
    name: str


class CryptoResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.CRYPTO
    source: str = "CoinGecko API"
    name: str


class SteamResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.STEAM
    source: str = "Steam Market"
    app_id: int
    name: str
