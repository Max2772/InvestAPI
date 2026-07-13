## 📦 Full Changelog
---

### 🆕 v1.3.4

#### 🐛 Bug Fixes:
* Remove steam browser headers from history endpoint. Earlier this caused `404` for all steam items.
---

### 🆕 v1.3.3

#### ✨ New Features:
* **`GET /search`** — autocomplete-style asset lookup by ticker, symbol, or name fragment. Query params: `q` (required), optional `type` (`stock` | `crypto` | `steam`), `limit` (default 20, max 50). Results are scored and sorted by relevance (prefix on ticker/symbol first, then substring in names). No Redis — in-memory search over static catalogs.
* **Search response models** in `app/schemas/search_responses.py` — discriminated hits: `StockSearchHit`, `CryptoSearchHit` (`name`, `symbol`, `full_name`), `SteamSearchHit` (`name`, `class_id`).
* **Asset catalogs** for search:
  - `STOCK_TICKERS` — `app/types/constants/stock_tickers.py` (ticker → company name)
  - `STEAM_NAMES` — `app/types/constants/steam_names.py` (CS2 & TF2 market hash names)
  - `CRYPTO_COINS` — existing registry, also used by search
* **`app/services/asset_search.py`** and tests in `tests/test_asset_search.py`.

---

### 🆕 v1.3.2

#### ✨ New Features:
* **Batch crypto spot prices** — `GET /crypto/{coins}` accepts a **comma-separated** list of CoinGecko **ids**, **symbols**, or **names** (e.g. `/crypto/bitcoin`, `/crypto/BTC,ETH,SOL`, `/crypto/bitcoin,ethereum,solana`). Response is `CryptoPricesResponse` with a `coins` array of `CryptoResponse` objects.
* **Single CoinGecko fast price request per batch** — uncached coins from one bulk client request are fetched together via CoinGecko `simple/price?ids=...&vs_currencies=usd`.
* **Background crypto cache warmer** — on app startup, a background task in `app/tasks/crypto_cache.py` runs every **15 minutes** (when Redis is available): one bulk request for the top **250** coins from `CRYPTO_COINS`, then writes each price to Redis under `coin:{id}`. First refresh runs **15 minutes after** startup (avoids external calls during tests).

---

### 🆕 v1.3.1

#### 🛠 Improvements:
* **Crypto coin resolution** — `/crypto/{coin}` and `/crypto/{coin}/history` accept CoinGecko **id**, **symbol**, or **display name** (e.g. `/crypto/TON`, `/crypto/Toncoin`, `/crypto/the-open-network` → the same asset).
* Replaced `CRYPTO_SYMBOLS` (`symbol → name`) with **`CRYPTO_COINS`** in `app/types/constants/crypto_symbols.py` — `(id, symbol, name)` tuples (~975 top coins by market cap).
* Added **`resolve_crypto_coin()`** in `app/utils/crypto_parser.py` — maps any alias to `ResolvedCrypto(id, symbol, full_name)`; used by `crypto_price.py` and `crypto_history.py` instead of the old `.lower()` name hack.
* Added new **Crypto response fields** (`CryptoResponse`, `CryptoHistoryResponse`):
  - `name` — CoinGecko id (e.g. `the-open-network`), used in Redis keys (`coin:{id}`, `coin:history:{id}`)
  - `symbol` — ticker (e.g. `TON`)
  - `full_name` — display name (e.g. `Toncoin`)
* Added **`tests/test_crypto_resolve.py`** for id/symbol/name resolution and slug fallback.

---

### 🆕 v1.3.0

#### ✨ New Features:
* **Price history endpoints** for building charts (daily interval `1d`):
  - `GET /stock/{ticker}/history?days=90` — Yahoo Finance via `yfinance` (`period=max`, sliced by `days`)
  - `GET /crypto/{coin}/history?days=30` — CoinGecko `market_chart` (full period cached, sliced by `days`)
  - `GET /steam/{app_id}/{market_hash_name}/history?days=90` — parsed from Steam Market listing HTML
* New schemas: `HistoryPoint`, `StockHistoryResponse`, `CryptoHistoryResponse`, `SteamHistoryResponse` in `app/schemas/history_responses.py`.
* Steam history parser (`app/utils/steam_history_parser.py`): supports legacy `var line1=...` and modern SSR embedded price data (`time`, `price_median`, `purchases`).
* Shared helpers in `app/utils/history_points.py`: `filter_points_by_days`, `collapse_to_daily`.

#### 🛠 Improvements:
* **Smart history caching** — one “max” dataset per asset in Redis, client `days` only filters the response:
  - `coin:history:{coin}` (CoinGecko, default 365 days)
  - `stock:history:{ticker}` (yfinance `max`)
  - `steam:history:{app_id}:{market_hash_name}` (full parsed history)
* Simplified `RedisClient`: universal `get_cache(key, model_cls)` and `set_cache(key, model, ttl)` with direct Pydantic JSON (removed `{asset_type, data}` wrapper).
* Split price services: `stock_price.py`, `crypto_price.py`, `steam_price.py`; history: `stock_history.py`, `crypto_history.py`, `steam_history.py`.
* Provider names and history settings centralized in `app/config.py` (`STOCK_PROVIDER_NAME`, `CRYPTO_HISTORY_PERIOD`, `STOCK_HISTORY_PERIOD`, `REDIS_*_HISTORY_INTERVAL`, etc.).
* Expanded test suite for history services, Steam HTML parser, and cache slicing.

---

### 🆕 v1.2.0
#### 🛠 Improvements:
* Refactored to **Layered Architecture** under `app/`:
  - `routers/` — HTTP endpoints and DI
  - `schemas/` — Pydantic response models
  - `services/` — business logic
  - `types/` — enums and constants
  - `database.py` — Redis client
  - `config.py` — environment settings and logging
  - `main.py` — FastAPI application
* Removed legacy `src/` package. Single entry point: `app/main.py`.
* Fixed `steam/` endpoint bug where skins with only median_price had **status 404**

---

### 🆕 v1.1.2
#### 🐛 Bug Fixes:
* Renamed `market_name` to `name` in `SteamResponse` for consistency across all response models. This fixes compatibility issues and standardizes asset naming.

---

### 🆕 v1.1.1
#### 🛠 Improvements:
* Renamed the name of services in `docker-compose.yaml` to `investapi-api` and `investapi-redis` to be more unique and prevent docker conflicts.

---

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