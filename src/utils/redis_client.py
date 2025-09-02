import os
import redis.asyncio as aioredis

from src.utils.logger import get_logger


_logger = get_logger()
_redis_client = None

async def init_redis():
    global _redis_client
    try:
        _redis_client = aioredis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', 6379)),
            password=os.environ.get('REDIS_PASSWORD', None),
            decode_responses=True
        )
        pong = await _redis_client.ping()
        if not pong:
            _redis_client = None
            _logger.info('Redis storage not found')
        else:
            _logger.info('Redis storage found')
    except Exception as e:
        _logger.error(f'Error while connecting to Redis: {e}')
        _redis_client = None

async def get_redis():
    return _redis_client