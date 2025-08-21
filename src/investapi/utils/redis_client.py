import os
from dotenv import load_dotenv
from redis.asyncio import Redis
from redis import RedisError

from investapi.utils.logger import get_logger


_logger = get_logger()
load_dotenv()

def init_redis_client():
    try:
        redis_client = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            decode_responses=True
        )
        _logger.info("Redis client initialized")
        return redis_client
    except RedisError as e:
        _logger.warning(f"Failed to connect to Redis: {e}")
        raise RuntimeError(f"Failed to connect to Redis: {e}")