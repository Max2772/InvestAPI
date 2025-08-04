from fastapi import FastAPI
from models.price_response import StockResponse, CryptoResponse, SteamResponse
from services import (get_stock_price, get_crypto_price, get_steam_item_price)

app = FastAPI(title="Investment API",
              description="API for fetching real-time prices of stocks, cryptocurrencies, and Steam items",
              version="1.0.0")

@app.get("/")
async def index():
    return {"Nothing here, look docs"}

@app.get("/stocks/{ticker}", response_model=StockResponse, summary="Get stock price")
async def stock_price(ticker: str):
    return await get_stock_price(ticker)

@app.get("/crypto/{coin}", response_model=CryptoResponse, summary="Get crypto price")
async def crypto_price(coin: str):
    return await get_crypto_price(coin)

@app.get("/steam/{app_id}/{market_hash_name}", response_model=SteamResponse, summary="Get steam item price")
async def steam_price(app_id: int, market_hash_name: str):
    return await get_steam_item_price(app_id, market_hash_name)