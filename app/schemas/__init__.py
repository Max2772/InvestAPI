from app.types.enums.enums import AssetType
from app.schemas.asset_responses import (
    BaseAssetResponse,
    StockResponse,
    CryptoResponse,
    SteamResponse,
)
from app.schemas.history_responses import (
    CryptoHistoryResponse,
    HistoryPoint,
    SteamHistoryResponse,
    StockHistoryResponse,
)

RESPONSE_BY_ASSET_TYPE: dict[AssetType, type[BaseAssetResponse]] = {
    AssetType.STOCK: StockResponse,
    AssetType.CRYPTO: CryptoResponse,
    AssetType.STEAM: SteamResponse,
}

__all__ = [
    "BaseAssetResponse",
    "StockResponse",
    "CryptoResponse",
    "SteamResponse",
    "HistoryPoint",
    "StockHistoryResponse",
    "CryptoHistoryResponse",
    "SteamHistoryResponse",
    "RESPONSE_BY_ASSET_TYPE",
]
