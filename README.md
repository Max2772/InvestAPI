# InvestAPI 📈

![version](https://img.shields.io/badge/version-1.1.0-blue)
[![Python Version](https://img.shields.io/badge/python-3.10--3.13-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com)

⚡ InvestAPI is a high-performance API built with [FastAPI](https://fastapi.tiangolo.com/) and [Redis](https://redis.io/) that provides up-to-date prices for stocks, ETFs, cryptocurrencies and Steam Market items. It leverages Redis for caching to ensure lightning-fast responses.

The project was created as a unified interface for the Telegram bot [@InvestingAPIBot](https://github.com/Max2772/InvestingAPIBot) to fetch and cache price data for various asset types, which are hard to source elsewhere. It can also be used for other services, such as websites or investment applications.

**Key Features:**
- 📊 Stock and ETF prices via `/stock/{ticker}` (data from [Yahoo Finance](https://finance.yahoo.com/)).
- 💰 Cryptocurrency prices via `/crypto/{coin}` (data from [CoinGecko](https://www.coingecko.com/)).
- 🎮 Steam item prices via `/steam/{app_id}/{market_name}` (data from [Steam Community Market](https://steamcommunity.com/market/)).
- 🚀 Fast caching with Redis to minimize external requests.
- 🌐 Asynchronous requests using `aiohttp` for high performance.

---

## [📦 Full Changelog](docs/ChangeLog.md)

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

## Installation 🛠️

### Requirements
- Python 3.10–3.13 (3.11 recommended for optimal compatibility with dependencies).
- Redis (installed via Docker or manually).
- Docker (optional, for running with `docker-compose`).
- OS: Tested on Windows; Linux support to be added later.

### Installation with Docker (Recommended)
1. Clone the repository:
   ```bash
   git clone https://github.com/Max2772/InvestAPI.git
   cd InvestAPI
   ```
2. Run the project with Docker:
   ```bash
   cd docker
   docker compose up --build -d
   ```
3. The API will be available at `http://localhost:8000`.

### Manual Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Max2772/InvestAPI.git
   cd InvestAPI
   ```
2. Set up a virtual environment and install dependencies. For production use (core dependencies) use `/requirements/prod`:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements/prod/requirements.txt
   ```
   For development (includes testing tools like `pytest`), use `/requirements/dev`:
   ```bash
   pip install -r requirements/dev/requirements.txt
   ```
3. Ensure Redis is installed and running.

4. Start the API:
   ```bash
   uvicorn main:app --reload
   ```
   or

   ```bash
   fastapi dev main.py
   ```
5. The API will be available at `http://localhost:8000`.

## Usage 📝

InvestAPI provides three main endpoints. Interactive documentation is available at `http://localhost:8000/docs`.

### Example Requests

1. **Stocks/ETFs**:
   ```bash
   curl http://localhost:8000/stock/MSFT
   ```
   Response:
   ```json
   {
   "asset_type":"stock",
   "price":459.51,
   "currency":"USD",
   "source":"Yahoo Finance",
   "cached_at":"2026-01-15T14:55:47.972055",
   "full_name":"Microsoft Corporation",
   "name":"MSFT"
   }
   ```

2. **Cryptocurrency**:
   ```bash
   curl http://localhost:8000/crypto/solana
   ```
   Response:
   ```json
   {
   "asset_type":"crypto",
   "price":144.0,
   "currency":"USD",
   "source":"CoinGecko",
   "cached_at":"2026-01-15T14:57:40.364132",
   "name":"solana"
   }
   ```

3. **Steam Items**:
   ```bash
   curl http://localhost:8000/steam/730/Danger Zone Case
   ```
   Response:
   ```json
   {
   "asset_type":"steam",
   "price":1.99,
   "currency":"USD",
   "source":"Steam Market",
   "cached_at":"2026-01-15T14:58:31.688942",
   "app_id":730,
   "market_name":"Danger Zone Case"
   }
   ```

### Example in Python
```python
import aiohttp

API_BASE_URL = "http://127.0.0.1:8000"

async def get_price(endpoint):
    async with aiohttp.ClientSession() as client:
        url = f"{API_BASE_URL}/{endpoint}"
        async with client.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("price")

# Example usage
price = await get_price("stock/AMD")
print(f"AMD price: {price}")
```

### Error Handling
If an asset is not found, the API returns a 404 error:
```json
{
   "error": "Not Found",
   "detail": "Stock APPL not found"
}
```

### Rate Limits
- No local rate limits (API runs on `localhost`).
- External APIs (Yahoo Finance, CoinGecko, Steam) may have their own limits, but Redis caching minimizes their impact.

## Configuration ⚙️

To configure the API, create a `.env` file in the project root or set environment variables:

```env
LOG_LEVEL=INFO

API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=TRUE

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password # Optional

REDIS_STOCK_INTERVAL=900
REDIS_CRYPTO_INTERVAL=300
REDIS_STEAM_INVERVAL=600
```

Alternatively, you can manually configure settings in `redis_client.py`. When using Docker, environment variables are set in `docker-compose.yaml`:

```yaml
services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: investapi
    env_file:
      - ../.env
    environment:
      REDIS_HOST: investapi_redis
      REDIS_PORT: 6379
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:alpine
    container_name: investapi_redis
    restart: unless-stopped
```

## Dependencies and Architecture 🏗️

### Dependencies

- `dotenv` — for loading environment variables from `.env` files.
- `uvicorn` — for running the FastAPI application server.
- `fastapi` — for building the API.
- `aiohttp` — for asynchronous external API requests.
- `yfinance` — for fetching stock and ETF data.
- `redis` — for Redis integration.
- For testing (development only): `pytest`, `pytest-asyncio`, `httpx` — for running API endpoint tests.

### Architecture
1. A user sends a request (e.g., `/stock/AMD`).
2. The API checks Redis for cached data via `RedisClient` class.
3. If cached, the data is returned immediately.
4. If not cached, the API fetches data from an external source (Yahoo Finance, CoinGecko, or Steam Market) using `aiohttp`.
5. The fetched data is cached in Redis for the set amount of seconds (from `.env`) and returned to the user.

The API can function without Redis, but caching significantly improves performance.

## License 📜 

This project is licensed under the MIT License. See the [License](LICENSE) file for details.

## Contact 📫

- GitHub: [@Max2772](https://github.com/Max2772)
- Email: [bib.maxim@gmail.com](mailto:bib.maxim@gmail.com)