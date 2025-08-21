import argparse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import redis

from investapi.utils import (setup_logger, set_log_level, handle_error_exception, init_redis_client)
from investapi.models import (StockResponse, CryptoResponse, SteamResponse)
from investapi.services import (get_stock_price, get_crypto_price, get_steam_item_price)


class InvestAPI(FastAPI):
    RedisStorage = None

    def __init__(self, redis: bool = True, *args, **kwargs):
        super().__init__(
            title="Investment API",
            description="API for fetching real-time prices of stocks, cryptocurrencies, and Steam items",
            version="1.0.0",
            *args, **kwargs
        )
        self.add_exception_handler(Exception, self.global_exception_handler)
        self.add_routes()
        if redis:
            self.add_redis_storage()

    def add_redis_storage(self):
        try:
            self.RedisStorage = init_redis_client()
        except redis.RedisError as e:
            self.RedisStorage = None

    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception):
        path_parts = request.url.path.split("/")
        source = path_parts[0] if path_parts else None

        http_exc = handle_error_exception(exc, source)

        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )

    async def stock(self, ticker: str):
        return await get_stock_price(ticker, self.RedisStorage)

    async def crypto(self, coin: str):
        return await get_crypto_price(coin, self.RedisStorage)

    async def steam(self, app_id: int, market_name: str):
        return await get_steam_item_price(app_id, market_name, self.RedisStorage)


    def add_routes(self):
        @self.get("/")
        async def index():
            return {"Nothing here, look docs"}


        @self.get("/stock/{ticker}", response_model=StockResponse, summary="Get stock price")
        async def stock_price(ticker: str):
            return await self.stock(ticker)


        @self.get("/crypto/{coin}", response_model=CryptoResponse, summary="Get crypto price")
        async def crypto_price(coin: str):
            return await self.crypto(coin)


        @self.get("/steam/{app_id}/{market_hash_name}", response_model=SteamResponse, summary="Get steam item price")
        async def steam_price(app_id: int, market_hash_name: str):
            return await self.steam(app_id, market_hash_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", type=str, default=None,
                        help="Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    if args.log_level:
        log_level = args.log_level.upper()
        set_log_level(log_level)

    _logger = setup_logger()

    app = InvestAPI(redis=True)

    uvicorn.run("investapi.app:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == '__main__':
    main()