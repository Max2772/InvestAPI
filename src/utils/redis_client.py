import os
from dotenv import load_dotenv
from redis.asyncio import Redis

from src.utils.logger import get_logger


load_dotenv()
logger = get_logger()
redis_client = None

async def init_redis():
    try:
        global redis_client
        redis_client = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
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