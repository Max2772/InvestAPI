import json
from typing import Union

import redis.asyncio as aioredis

from src.env import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from src.types import ttl_dict
from src.logger import logger
from src.models import StockResponse, CryptoResponse, SteamResponse
from src.types import AssetType


class RedisClient:
    def __init__(self):
        self._client = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )

    @property
    def client(self):
        return self._client

    async def test_connection(self) -> bool:
        try:
            pong = await self._client.ping()

            if not pong:
                logger.info('Redis storage not found')
                return False

            logger.info('Redis storage found')
            return True

        except Exception as e:
            logger.error(f'Error testing Redis connection: {e}')
            return False

    async def get_cache(
            self,
            cache_key: str
    ) -> Union[StockResponse, CryptoResponse, SteamResponse, None]:
        try:
            cache = await self._client.get(cache_key)

            if not cache:
                logger.info(f'Cache {cache_key} not found')
                return None
            logger.info(f"Cache match for {cache_key}")

            payload = json.loads(cache)
            asset_type = AssetType(payload.get('asset_type'))
            asset_data = payload.get('data')

            if not asset_type or not asset_data:
                logger.warning(f'Invalid payload for {cache_key}')
                return None

            if asset_type == AssetType.STOCK:
                return StockResponse.model_validate(asset_data)
            elif asset_type == AssetType.CRYPTO:
                return CryptoResponse.model_validate(asset_data)
            elif asset_type == AssetType.STEAM:
                return SteamResponse.model_validate(asset_data)
            else:
                logger.warning(f'Unknown asset_type: {asset_type} for {cache_key}')
                return None

        except Exception as e:
            logger.error(f'Error while getting {cache_key} cache: {e}')
            return None

    async def set_cache(
            self,
            cache_key: str,
            response: Union[StockResponse, CryptoResponse, SteamResponse]
    ) -> None:
        try:
            payload = {
                "asset_type": response.asset_type.value,
                "data": response.model_dump(mode="json")
            }

            ttl = ttl_dict.get(response.asset_type, 900)

            if ttl > 0:
                await self._client.setex(cache_key, ttl, json.dumps(payload))
                logger.info(f'{cache_key} cache set for {ttl} seconds')
            else:
                logger.warning(f"{cache_key} not cached because TTL={ttl}")

        except Exception as e:
            logger.error(f'Error while setting {cache_key} cache: {e}')
