from app.types.enums.enums import AssetType
from app.schemas.asset_responses import (
    BaseAssetResponse,
    StockResponse,
    CryptoResponse,
    SteamResponse,
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
    "RESPONSE_BY_ASSET_TYPE",
]
