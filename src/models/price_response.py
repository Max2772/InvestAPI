from datetime import datetime

from pydantic import BaseModel

class StockResponse(BaseModel):
    name: str
    price: float
    currency: str
    source: str
    cached_at: datetime

class CryptoResponse(BaseModel):
    name: str
    price: float
    currency: str
    source: str
    cached_at: datetime

class SteamResponse(BaseModel):
    app_id: int
    item_name: str
    price: float
    currency: str
    source: str
    cached_at: datetime