from typing import Dict
from src.env import REDIS_STOCK_INTERVAL, REDIS_CRYPTO_INTERVAL, REDIS_STEAM_INTERVAL
from src.types.response_enums import AssetType

ttl_dict: Dict[AssetType, int] = {
    AssetType.STOCK: REDIS_STOCK_INTERVAL,
    AssetType.CRYPTO: REDIS_CRYPTO_INTERVAL,
    AssetType.STEAM: REDIS_STEAM_INTERVAL
}