from typing import Annotated

import aiohttp
from fastapi import Depends, Request

from app.database import RedisClient


def get_redis_client(request: Request) -> RedisClient | None:
    return request.app.state.redis_client


def get_http_session(request: Request) -> aiohttp.ClientSession:
    return request.app.state.http_session


RedisDep = Annotated[RedisClient | None, Depends(get_redis_client)]
HttpSessionDep = Annotated[aiohttp.ClientSession, Depends(get_http_session)]
