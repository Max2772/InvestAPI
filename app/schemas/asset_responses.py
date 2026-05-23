from datetime import datetime

from pydantic import BaseModel

from app.config import STOCK_PROVIDER_NAME, CRYPTO_PROVIDER_NAME, STEAM_PROVIDER_NAME
from app.types.enums.enums import AssetType


class BaseAssetResponse(BaseModel):
    price: float
    currency: str = "USD"
    cached_at: datetime


class StockResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.STOCK
    full_name: str
    source: str = STOCK_PROVIDER_NAME
    name: str


class CryptoResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.CRYPTO
    source: str = CRYPTO_PROVIDER_NAME
    name: str


class SteamResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.STEAM
    source: str = STEAM_PROVIDER_NAME
    app_id: int
    name: str
