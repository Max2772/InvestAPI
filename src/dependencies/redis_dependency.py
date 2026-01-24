from typing import Annotated, Optional
from fastapi import Depends, Request
from src.utils.redis_client import RedisClient


def get_redis_client(request: Request) -> Optional[RedisClient]:
    return request.app.state.redis_client

redisDep = Annotated[Optional[RedisClient], Depends(get_redis_client)]
