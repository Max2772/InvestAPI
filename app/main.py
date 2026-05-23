from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import API_HOST, API_PORT, API_RELOAD, LOG_LEVEL
from app.database import RedisClient
from app.routers import router
from app.utils.exceptions import AssetNotFoundError, ExternalServiceError
from app.utils.logging import logger


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

    app.state.http_session = aiohttp.ClientSession()

    yield

    await app.state.http_session.close()

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
            "API for fetching real-time prices and daily price history "
            "of stocks, cryptocurrencies, and Steam assets"
        ),
        version="1.3.0",
        lifespan=lifespan,
    )
    application.include_router(router)

    @application.exception_handler(AssetNotFoundError)
    async def asset_not_found_handler(
        _request: Request, ex: AssetNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "detail": ex.detail},
        )

    @application.exception_handler(ExternalServiceError)
    async def external_service_handler(
        _request: Request, ex: ExternalServiceError
    ) -> JSONResponse:
        error_label = "Bad Gateway" if ex.status_code == 502 else "External Service Error"
        return JSONResponse(
            status_code=ex.status_code,
            content={"error": error_label, "detail": ex.detail},
        )

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
