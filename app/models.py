from enum import Enum

from app.config import REDIS_STOCK_INTERVAL, REDIS_CRYPTO_INTERVAL, REDIS_STEAM_INTERVAL


class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    STEAM = "steam"


# TTL (seconds) for Redis cache by asset type.
TTL_BY_ASSET_TYPE: dict[AssetType, int] = {
    AssetType.STOCK: REDIS_STOCK_INTERVAL,
    AssetType.CRYPTO: REDIS_CRYPTO_INTERVAL,
    AssetType.STEAM: REDIS_STEAM_INTERVAL,
}
