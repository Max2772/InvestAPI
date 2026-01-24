## 📦 Full Changelog

---

### 🆕 v1.1.0
### 🆕 v1.1.0

#### ✨ New Features:
* Added `full_name` field to the `StockResponse` model, providing the full company name for stocks and ETFs fetched from Yahoo Finance.
* Introduced a custom `AssetType` Enum to categorize responses (STOCK, CRYPTO, STEAM), improving type safety and Redis cache handling.
* Implemented Dependency Injection (`redisDep`) for Redis client, allowing concise and reusable injection into endpoints `/stock`, `/crypto`, and `/steam`.
* Updated `.env` configuration file with new structure and defaults for easier setup, including separate cache intervals for each asset type (STOCK, CRYPTO, STEAM) to allow developers to customize TTLs more conveniently in one central location:
  ```
   LOG_LEVEL=INFO
   API_HOST=0.0.0.0
   API_PORT=8000
   API_RELOAD=TRUE
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   REDIS_STOCK_INTERVAL=900
   REDIS_CRYPTO_INTERVAL=300
   REDIS_STEAM_INTERVAL=600
  ```
  Defaults are handled in `src/env.py` for all parameters, ensuring fallback values if not specified.
* Centralized Redis operations with a single `RedisClient` class in `src/services`, simplifying code, reducing duplication, and providing unified methods for connection testing, cache getting/setting.
* Added basic API testing for all endpoints using `pytest`, `pytest-asyncio` and `httpx`. Tests cover the root endpoint and asset-specific endpoints like `/stock`, `/crypto`, and `/steam`. To run tests, install dev dependencies and execute `pytest -v` from the project root.
* Reorganized requirements files into a `/requirements` directory with `/prod` and `/dev` subfolders. Each contains `requirements.txt` and `requirements.in`:
  - `/prod`: Core dependencies for running the API:
    ```
    dotenv
    uvicorn
    fastapi
    aiohttp
    yfinance
    redis
    ```
  - `/dev`: Includes prod dependencies plus `pytest`, `pytest-asyncio`, and `httpx` for testing.

#### 🛠 Improvements:
* Replaced deprecated `@app.on_event("startup")` with modern `@asynccontextmanager` and `async def lifespan()` for Redis initialization and connection checking, enhancing compatibility and lifecycle management.
* Optimized dependencies by removing unnecessary libraries, including `fastapi[standard]` (which pulled ~100 extra dependencies, inflating virtual environments to ~500MB). Updated `requirements.in` to a minimal set.
* Removed `ArgumentParser` to eliminate IDE conflicts and unpredictable logging behavior. Logging level is now solely controlled via `LOG_LEVEL` in `.env`, which also propagates to Uvicorn's `log_level` for unified configuration.
* Refactored Pydantic models for responses:
  - Base `BaseAssetResponse` with shared fields like `asset_type`, `price`, `currency`, `source`, and `cached_at`.
  - Asset models (`StockResponse`, `CryptoResponse`, `SteamResponse`) now include `asset_type` for Redis to determine payload type during cache retrieval.
* Comprehensive refactoring of the codebase for cleaner structure, improved readability, and reduced redundancy across services and endpoints.

#### 🐛 Bug Fixes:
* Fixed cache serialization issue in Redis for the `/crypto` endpoint, where the previous `await redis_client.setex(cache_key, 900, json.dumps(response_data.model_dump(), default=str))` broke deserialization. Now handled properly via unified `RedisClient` methods with JSON payloads including `asset_type`.
---