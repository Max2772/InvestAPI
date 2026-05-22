from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config import API_HOST, API_PORT, API_RELOAD, LOG_LEVEL, logger
from app.database import RedisClient
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.redis_client = RedisClient()
        if await app.state.redis_client.test_connection():
            logger.info("Redis connection established successfully.")
        else:
            logger.warning("Redis connection failed. Falling back to no-cache mode.")
            app.state.redis_client = None
    except Exception as e:
        logger.error(f"Critical error during Redis startup: {e}")
        app.state.redis_client = None

    yield

    if app.state.redis_client:
        try:
            await app.state.redis_client.client.close()
            logger.info("Redis connection closed.")
        except Exception as e:
            logger.warning(f"Error closing Redis: {e}")


def create_app() -> FastAPI:
    application = FastAPI(
        title="InvestAPI",
        description=(
            "API for fetching real-time prices of stocks, cryptocurrencies, and Steam assets"
        ),
        version="1.2.0",
        lifespan=lifespan,
    )
    application.include_router(router)
    return application


app = create_app()


if __name__ == "__main__":
    logger.info("Staring InvestAPI server...")
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level=LOG_LEVEL.lower(),
        access_log=True,
    )
