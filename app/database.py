from typing import TypeVar

import redis.asyncio as aioredis
from pydantic import BaseModel

from app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from app.utils.logging import logger

T = TypeVar("T", bound=BaseModel)


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

    async def get_cache(self, cache_key: str, model_cls: type[T]) -> T | None:
        try:
            cache = await self._client.get(cache_key)
            if not cache:
                logger.info(f"Cache {cache_key} not found")
                return None

            logger.info(f"Cache match for {cache_key}")
            return model_cls.model_validate_json(cache)
        except Exception as e:
            logger.error(f"Error while getting {cache_key} cache: {e}")
            return None

    async def set_cache(self, cache_key: str, model: BaseModel, ttl: int) -> None:
        try:
            if ttl > 0:
                await self._client.setex(cache_key, ttl, model.model_dump_json())
                logger.info(f"{cache_key} cache set for {ttl} seconds")
            else:
                logger.warning(f"{cache_key} not cached. TTL must be greater than 0")
        except Exception as e:
            logger.error(f"Error while setting {cache_key} cache: {e}")
