import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL: str = (os.getenv("LOG_LEVEL") or "INFO").upper()

API_HOST: str = os.getenv("API_HOST") or "0.0.0.0"
API_PORT: int = int(os.getenv("API_PORT") or 8000)
API_RELOAD: bool = (os.getenv("API_RELOAD").upper() or "TRUE") in ("TRUE", "YES", "ON", "1")

REDIS_HOST: str = os.getenv("REDIS_HOST") or "0.0.0.0"
REDIS_PORT: int = int(os.getenv("REDIS_PORT") or 6379)
REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD") or None

REDIS_STOCK_INTERVAL: int = int(os.getenv("REDIS_STOCK_INTERVAL") or 900)
REDIS_CRYPTO_INTERVAL: int = int(os.getenv("REDIS_CRYPTO_INTERVAL") or 300)
REDIS_STEAM_INTERVAL: int = int(os.getenv("REDIS_STEAM_INTERVAL") or 900)