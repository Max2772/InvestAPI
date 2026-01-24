from datetime import datetime
from pydantic import BaseModel
from src.types import AssetType

class BaseAssetResponse(BaseModel):
    asset_type: AssetType
    price: float
    currency: str
    source: str
    cached_at: datetime

class StockResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.STOCK
    full_name: str
    name: str

class CryptoResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.CRYPTO
    name: str

class SteamResponse(BaseAssetResponse):
    asset_type: AssetType = AssetType.STEAM
    app_id: int
    market_name: str