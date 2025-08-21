import os
from dotenv import load_dotenv
import redis


load_dotenv()

def init_redis_client():
    try:
        redis_client =  redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            decode_responses=True
        )
        redis_client.ping()
        return redis_client
    except redis.RedisError as e:
        return None

redis_client = init_redis_client()

