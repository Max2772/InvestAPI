# InvestAPI 📈

![version](https://img.shields.io/badge/version-1.3.1-blue)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com)

⚡ InvestAPI is a high-performance API built with [FastAPI](https://fastapi.tiangolo.com/) and [Redis](https://redis.io/) that provides up-to-date prices and **daily price history** for stocks, ETFs, cryptocurrencies, and Steam Market items. Redis caches provider responses to keep latency low and reduce external API load.

The project was created as a unified interface for the Telegram bot [@InvestingAPIBot](https://github.com/Max2772/InvestingAPIBot) to fetch and cache price data for various asset types. It can also be used for websites, dashboards, or investment applications.

**Key Features:**
- 📊 Stock and ETF **spot prices** via `/stock/{ticker}` ([Yahoo Finance](https://finance.yahoo.com/) / `yfinance`).
- 📈 Stock **history** via `/stock/{ticker}/history?days=90` (daily candles, `1d`).
- 💰 Cryptocurrency **spot prices** via `/crypto/{coin}` ([CoinGecko](https://www.coingecko.com/)) — `{coin}` accepts **id**, **symbol**, or **name** (e.g. `the-open-network`, `TON`, `Toncoin`).
- 📉 Crypto **history** via `/crypto/{coin}/history?days=30` (daily points, same aliases).
- 🪙 Crypto responses expose **`name`** (CoinGecko id), **`symbol`** (ticker), and **`full_name`** (display name).
- 🎮 Steam item **spot prices** via `/steam/{app_id}/{market_hash_name}` ([Steam Community Market](https://steamcommunity.com/market/)).
- 📊 Steam item **history** via `/steam/{app_id}/{market_hash_name}/history?days=90` (parsed from listing page HTML).
- 🚀 Redis caching with “fetch max once, slice by `days`” for history endpoints.
- 🌐 Async HTTP via `aiohttp` for crypto and Steam.

---

## [📦 Full Changelog](docs/ChangeLog.md)

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

## Installation 🛠️

### Requirements
- Python 3.11+ (see `requires-python` in `pyproject.toml`).
- [uv](https://docs.astral.sh/uv/) — dependency and environment manager.
- Redis (Docker or local).
- Docker (optional).

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
2. Install dependencies:
   ```bash
   uv sync
   ```
   Production only:
   ```bash
   uv sync --no-dev
   ```
3. Ensure Redis is running.
4. Start the API:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   or
   ```bash
   uv run fastapi dev app/main.py
   ```
5. Open `http://localhost:8000/docs` for interactive API documentation.

## Usage 📝

### Spot prices

1. **Stocks / ETFs**
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

2. **Cryptocurrency**
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
   "name": "solana",
   "symbol": "SOL",
   "full_name": "Solana"
   }
   ```

3. **Steam items**
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

### Price history

1. **Stocks / ETFs**
   ```bash
   curl "http://localhost:8000/stock/MSFT/history?days=3"
   ```
   Response:
   ```json
   {
   "asset_type":"stock",
   "name":"MSFT",
   "full_name":"Microsoft Corporation",
   "interval":"1d",
   "points":[
      {"timestamp":"2026-05-20T00:00:00","price":452.10,"volume":22150000.0},
      {"timestamp":"2026-05-21T00:00:00","price":455.80,"volume":19830000.0},
      {"timestamp":"2026-05-22T00:00:00","price":459.51,"volume":21400000.0}
   ],
   "source":"Yahoo Finance API",
   "cached_at":"2026-05-23T12:00:00"
   }
   ```

2. **Cryptocurrency**
   ```bash
   curl "http://localhost:8000/crypto/TON/history?days=3"
   ```
   Response:
   ```json
   {
   "asset_type":"crypto",
   "name":"the-open-network",
   "symbol":"TON",
   "full_name":"Toncoin",
   "interval":"1d",
   "points":[
      {"timestamp":"2026-05-20T00:00:00","price":1.89,"volume":210000000.0},
      {"timestamp":"2026-05-21T00:00:00","price":1.90,"volume":195000000.0},
      {"timestamp":"2026-05-22T00:00:00","price":1.91,"volume":188000000.0}
   ],
   "source":"Coin Gecko API",
   "cached_at":"2026-05-23T12:00:00"
   }
   ```

3. **Steam items**
   ```bash
   curl "http://localhost:8000/steam/730/Danger%20Zone%20Case/history?days=3"
   ```
   Response:
   ```json
   {
   "asset_type":"steam",
   "app_id":730,
   "name":"Danger Zone Case",
   "interval":"1d",
   "points":[
      {"timestamp":"2026-05-20T00:00:00","price":1.95,"volume":1250.0},
      {"timestamp":"2026-05-21T00:00:00","price":1.97,"volume":1180.0},
      {"timestamp":"2026-05-22T00:00:00","price":1.99,"volume":1320.0}
   ],
   "source":"Steam Market",
   "cached_at":"2026-05-23T12:00:00"
   }
   ```

### Example in Python
```python
import aiohttp

API_BASE_URL = "http://127.0.0.1:8000"

async def get_spot_price(endpoint: str) -> float:
    async with aiohttp.ClientSession() as client:
        async with client.get(f"{API_BASE_URL}/{endpoint}") as response:
            response.raise_for_status()
            return (await response.json())["price"]

async def get_history(endpoint: str) -> list[dict]:
    async with aiohttp.ClientSession() as client:
        async with client.get(f"{API_BASE_URL}/{endpoint}") as response:
            response.raise_for_status()
            return (await response.json())["points"]

# Spot
price = await get_spot_price("stock/AMD")

# History for a chart (symbol, name, or id all work)
points = await get_history("crypto/TON/history?days=30")
```

### Error Handling
If an asset is not found:
```json
{
  "error": "Not Found",
  "detail": "Stock APPL not found"
}
```

### Rate Limits
- No built-in rate limits on the API itself.
- External providers (Yahoo, CoinGecko, Steam) have their own limits; Redis caching reduces how often they are called.

## Configuration ⚙️

Create a `.env` file in the project root:

```env
LOG_LEVEL=INFO

API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=TRUE

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Spot price cache TTL (seconds)
REDIS_STOCK_INTERVAL=900
REDIS_CRYPTO_INTERVAL=300
REDIS_STEAM_INTERVAL=900

# History cache TTL (seconds)
REDIS_STOCK_HISTORY_INTERVAL=86400
REDIS_CRYPTO_HISTORY_INTERVAL=86400
REDIS_STEAM_HISTORY_INTERVAL=86400

# How much history to fetch from providers (before slicing by ?days=)
CRYPTO_HISTORY_PERIOD=365
STOCK_HISTORY_PERIOD=max
```

With Docker, use `docker/docker-compose.yaml` and set `REDIS_HOST=investapi_redis` for the API service.

## Dependencies and Architecture 🏗️

### Dependencies

- `fastapi`, `uvicorn` — API server
- `aiohttp` — async HTTP to CoinGecko and Steam
- `yfinance` — stocks and history
- `redis` — caching
- `dotenv` — configuration
- Dev: `pytest`, `pytest-asyncio`, `httpx`

### Architecture (Layered)

```
app/
├── routers/              # HTTP routes (spot + history)
├── schemas/              # Pydantic models (asset_responses, history_responses)
├── services/             # stock_price, stock_history, crypto_price, ...
├── types/constants/      # CRYPTO_COINS registry (id, symbol, name)
├── utils/                # crypto_parser, history_points, steam_history_parser, errors
├── database.py           # RedisClient (get_cache / set_cache)
├── config.py             # Settings from .env
└── main.py               # FastAPI app
```

**History request flow** (`GET /crypto/TON/history?days=30`):

1. **Router** — validates `days`, injects Redis and `aiohttp` session.
2. **`crypto_parser`** — `resolve_crypto_coin("TON")` → `id=the-open-network`, `symbol=TON`, `full_name=Toncoin`.
3. **Service** — reads `coin:history:the-open-network` from Redis; on miss, fetches up to `CRYPTO_HISTORY_PERIOD` days from CoinGecko, normalizes to daily, stores full series.
4. **Utils** — `filter_points_by_days` returns the last N days to the client.
5. **Schema** — `CryptoHistoryResponse` with `name`, `symbol`, `full_name`, and `points[]`.

The API works without Redis (no-cache mode) but repeating responses will be a lot slower.

## Testing

```bash
uv run pytest -v
```

## License 📜

This project is licensed under the MIT License. See the [License](LICENSE) file for details.

## Contact 📫

- GitHub: [@Max2772](https://github.com/Max2772)
- Email: [max@bibikau.org](mailto:max@bibikau.org)