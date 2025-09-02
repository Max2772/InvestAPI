from typing import Optional
import os

import redis.asyncio as aioredis

from src.utils.logger import get_logger


logger = get_logger()
redis_client = None

async def init_redis():
    global redis_client
    try:
        redis_client = aioredis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', 6379)),
            password=os.environ.get('REDIS_PASSWORD', None),
            decode_responses=True
        )
        pong = await redis_client.ping()
        if not pong:
            redis_client = None
            logger.info('Redis storage not found')
        else:
            logger.info('Redis storage found')
    except Exception as e:
        logger.error(f'Error while connecting to Redis: {e}')
        redis_client = None

async def get_redis() -> Optional[aioredis.Redis]:
    return redis_client