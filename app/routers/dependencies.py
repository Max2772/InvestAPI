from typing import Annotated

from fastapi import Depends, Request

from app.database import RedisClient


def get_redis_client(request: Request) -> RedisClient | None:
    return request.app.state.redis_client


RedisDep = Annotated[RedisClient | None, Depends(get_redis_client)]
