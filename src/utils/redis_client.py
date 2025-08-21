import os
from dotenv import load_dotenv
from redis.asyncio import Redis

from src.utils import get_logger


logger = get_logger()
load_dotenv()


redis_client = Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

logger.info("Redis Client Initialized")