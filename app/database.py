import json
from typing import Union

import redis.asyncio as aioredis

from app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, logger
from app.models import AssetType, TTL_BY_ASSET_TYPE
from app.schemas import RESPONSE_BY_ASSET_TYPE
from app.schemas.asset_responses import BaseAssetResponse


class RedisClient:
    def __init__(self):
        self._client = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )

    @property
    def client(self):
        return self._client

    async def test_connection(self) -> bool:
        try:
            pong = await self._client.ping()
            if not pong:
                logger.info("Redis storage not found")
                return False
            logger.info("Redis storage found")
            return True
        except Exception as e:
            logger.error(f"Error testing Redis connection: {e}")
            return False

    async def get_cache(
        self,
        cache_key: str,
    ) -> Union[BaseAssetResponse, None]:
        try:
            cache = await self._client.get(cache_key)
            if not cache:
                logger.info(f"Cache {cache_key} not found")
                return None

            logger.info(f"Cache match for {cache_key}")
            payload = json.loads(cache)
            asset_type = AssetType(payload.get("asset_type"))
            asset_data = payload.get("data")

            if not asset_data:
                logger.warning(f"Invalid payload for {cache_key}")
                return None

            response_cls = RESPONSE_BY_ASSET_TYPE.get(asset_type)
            if response_cls is None:
                logger.warning(f"Unknown asset_type: {asset_type} for {cache_key}")
                return None

            return response_cls.model_validate(asset_data)
        except Exception as e:
            logger.error(f"Error while getting {cache_key} cache: {e}")
            return None

    async def set_cache(
        self,
        cache_key: str,
        response: Union[BaseAssetResponse],
    ) -> None:
        try:
            payload = {
                "asset_type": response.asset_type.value,
                "data": response.model_dump(mode="json"),
            }
            ttl = TTL_BY_ASSET_TYPE.get(response.asset_type, 900)

            if ttl > 0:
                await self._client.setex(cache_key, ttl, json.dumps(payload))
                logger.info(f"{cache_key} cache set for {ttl} seconds")
            else:
                logger.warning(f"{cache_key} not cached. TTL must be greater than 0")
        except Exception as e:
            logger.error(f"Error while setting {cache_key} cache: {e}")
