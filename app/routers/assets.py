from fastapi import APIRouter, Query
from starlette.responses import RedirectResponse

from app.routers.dependencies import HttpSessionDep, RedisDep
from app.schemas import (
    StockResponse,
    CryptoResponse,
    SteamResponse,
    StockHistoryResponse,
    CryptoHistoryResponse,
    SteamHistoryResponse,
)
from app.services import (
    get_stock_price,
    get_crypto_price,
    get_steam_item_price,
    get_stock_history,
    get_crypto_history,
    get_steam_item_history,
)

router = APIRouter()


@router.get("/")
async def index():
    return RedirectResponse(url="/docs")


@router.get(
    "/stock/{ticker}",
    response_model=StockResponse,
    tags=["Stocks"],
    summary="Get stock price",
)
async def stock_price(ticker: str, redis_client: RedisDep):
    return await get_stock_price(ticker, redis_client)


@router.get(
    "/stock/{ticker}/history",
    response_model=StockHistoryResponse,
    tags=["Stocks"],
    summary="Get stock price history",
)
async def stock_history(
    ticker: str,
    redis_client: RedisDep,
    days: int = Query(90, ge=1, le=3650, description="Number of days of history to return"),
):
    return await get_stock_history(ticker, days, redis_client)


@router.get(
    "/crypto/{coin}",
    response_model=CryptoResponse,
    tags=["Crypto"],
    summary="Get crypto price",
)
async def crypto_price(
        coin: str,
        redis_client: RedisDep,
        http_session: HttpSessionDep
):
    return await get_crypto_price(coin, redis_client, http_session)


@router.get(
    "/crypto/{coin}/history",
    response_model=CryptoHistoryResponse,
    tags=["Crypto"],
    summary="Get cryptocurrency price history",
)
async def crypto_history(
    coin: str,
    redis_client: RedisDep,
    http_session: HttpSessionDep,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
):
    return await get_crypto_history(coin, days, redis_client, http_session)


@router.get(
    "/steam/{app_id}/{market_hash_name}",
    response_model=SteamResponse,
    tags=["Steam"],
    summary="Get steam item price",
)
async def steam_price(
    app_id: int,
    market_hash_name: str,
    redis_client: RedisDep,
    http_session: HttpSessionDep,
):
    return await get_steam_item_price(app_id, market_hash_name, redis_client, http_session)


@router.get(
    "/steam/{app_id}/{market_hash_name}/history",
    response_model=SteamHistoryResponse,
    tags=["Steam"],
    summary="Get steam item price history",
)
async def steam_history(
    app_id: int,
    market_hash_name: str,
    redis_client: RedisDep,
    http_session: HttpSessionDep,
    days: int = Query(90, ge=1, le=3650, description="Number of days of history to return"),
):
    return await get_steam_item_history(
        app_id, market_hash_name, days, redis_client, http_session
    )
