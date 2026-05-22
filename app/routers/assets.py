from fastapi import APIRouter
from starlette.responses import RedirectResponse

from app.routers.dependencies import HttpSessionDep, RedisDep
from app.schemas import StockResponse, CryptoResponse, SteamResponse
from app.services import get_stock_price, get_crypto_price, get_steam_item_price

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
