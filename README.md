# InvestAPI 📈

![version](https://img.shields.io/badge/version-1.2.0-blue)
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

### 🆕 v1.2.0
#### 🛠 Improvements:
* Refactored to **Layered Architecture** under `app/`:
  - `routers/` — HTTP endpoints and DI
  - `schemas/` — Pydantic response models
  - `services/` — business logic
  - `models.py` — `AssetType` enum and cache TTL
  - `database.py` — Redis client
  - `config.py` — environment settings and logging
  - `main.py` — FastAPI application
* Removed legacy `src/` package. Single entry point: `app/main.py`.
* Fixed `steam/` endpoint bug where skins with only median_price had **status 404**

---

## Installation 🛠️

### Requirements
- Python 3.11+ (see `requires-python` in `pyproject.toml`).
- [uv](https://docs.astral.sh/uv/) — dependency and environment manager.
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
2. Install dependencies with [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```
   Production only (no dev tools such as `pytest`):
   ```bash
   uv sync --no-dev
   ```
   `uv sync` reads `pyproject.toml` and `uv.lock`, creates a virtual environment, and installs pinned packages.
3. Ensure Redis is installed and running.

4. Start the API:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   or

   ```bash
   uv run fastapi dev app/main.py
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
   "name":"Danger Zone Case"
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
  investapi-api:
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
      - investapi-redis
    restart: unless-stopped

  investapi-redis:
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

### Architecture (Layered)

```
app/
├── routers/       # HTTP routes and dependencies
├── schemas/       # Pydantic API models
├── services/      # Business logic (fetch prices, cache orchestration)
├── constants/     # Static reference data (e.g. crypto symbol map)
├── utils/         # Shared helpers (HTTP error mapping)
├── models.py      # Domain enums and cache TTL (ORM-ready)
├── database.py    # Redis client (persistence layer)
├── config.py      # Settings and logging
└── main.py        # FastAPI app entry point
```

**Request flow** (`GET /stock/AMD`):

1. **Router** — validates input, injects Redis via `RedisDep`.
2. **Service** — checks cache, calls Yahoo Finance if needed, stores result.
3. **Database** — `RedisClient` get/set cache.
4. **Schema** — `StockResponse` returned to the client.

Run: `uv run uvicorn app.main:app --reload`

The API can function without Redis, but caching significantly improves performance.

## License 📜 

This project is licensed under the MIT License. See the [License](LICENSE) file for details.

## Contact 📫

- GitHub: [@Max2772](https://github.com/Max2772)
- Email: [bib.maxim@gmail.com](mailto:bib.maxim@gmail.com)