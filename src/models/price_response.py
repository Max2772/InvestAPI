from datetime import datetime

from pydantic import BaseModel


class BaseAssetResponse(BaseModel):
    price: float
    currency: str
    source: str
    cached_at: datetime

class StockResponse(BaseAssetResponse):
    name: str

class CryptoResponse(BaseAssetResponse):
    name: str

class SteamResponse(BaseAssetResponse):
    app_id: int
    market_name: str