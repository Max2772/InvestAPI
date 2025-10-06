# InvestAPI 📈

API for fetching real-time prices of stocks, ETFs, cryptocurrencies, and Steam items, powered by FastAPI and Redis caching.

[![Python Version](https://img.shields.io/badge/python-3.10--3.13-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com)

## Description

InvestAPI is a high-performance API built with [FastAPI](https://fastapi.tiangolo.com/) that provides up-to-date prices for stocks, ETFs, cryptocurrencies, and Steam items. It leverages Redis for caching to ensure lightning-fast responses ⚡.

The project was created as a unified interface for the Telegram bot `@InvestingAPIBot` to fetch and cache price data, particularly for Steam items, which are hard to source elsewhere. It can also be used for other services, such as websites or investment applications.

**Key Features:**
- 📊 Stock and ETF prices via `/stock/{ticker}` (data from [Yahoo Finance](https://finance.yahoo.com/)).
- 💰 Cryptocurrency prices via `/crypto/{coin}` (data from [CoinGecko](https://www.coingecko.com/)).
- 🎮 Steam item prices via `/steam/{app_id}/{market_name}` (data from [Steam Community Market](https://steamcommunity.com/market/)).
- 🚀 Fast caching with Redis to minimize external requests.
- 🌐 Asynchronous requests using `aiohttp` for high performance.

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
2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
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

InvestAPI provides three main endpoints. Interactive documentation is available at `http://localhost:8000/docs` (generated automatically by FastAPI).

### Example Requests

1. **Stocks/ETFs**:
   ```bash
   curl http://localhost:8000/stock/MSFT
   ```
   Response:
   ```json
   {"name":"MSFT","price":507.43,"currency":"USD","source":"Yahoo Finance","cached_at":"2025-08-22T19:15:48.553922"}
   ```

2. **Cryptocurrency**:
   ```bash
   curl http://localhost:8000/crypto/solana
   ```
   Response:
   ```json
   {"name":"solana","price":196.99,"currency":"USD","source":"CoinGecko","cached_at":"2025-08-22T19:16:40.148279"}
   ```

3. **Steam Items**:
   ```bash
   curl http://localhost:8000/steam/730/Danger Zone Case
   ```
   Response:
   ```json
   {"app_id":730,"item_name":"Danger Zone Case","price":2.38,"currency":"USD","source":"Steam Market","cached_at":"2025-08-22T19:17:00.696130"}
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
{"error":"Not Found","detail":"Stock APPL not found"}
```

### Rate Limits
- No local rate limits (API runs on `localhost`).
- External APIs (Yahoo Finance, CoinGecko, Steam) may have their own limits, but Redis caching (default 900 seconds) minimizes their impact.

## Configuration ⚙️

To configure Redis, create a `.env` file in the project root or set environment variables:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password  # Optional
```

Alternatively, you can manually configure settings in `redis_client.py`. When using Docker, environment variables are set in `docker-compose.yaml`:

```yaml
services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: investapi
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
  redis:
    image: redis
    container_name: investapi_redis
    ports:
      - "127.0.0.1:6379:6379"
```

## Dependencies and Architecture 🏗️

### Dependencies
- `fastapi[standard]` — for building the API.
- `redis` — for Redis integration.
- `aiohttp` — for asynchronous external API requests.
- `yfinance` — for fetching stock and ETF data.
- `pip-tools` — for dependency management.

### Architecture
1. A user sends a request (e.g., `/stock/AMD`).
2. The API checks Redis for cached data.
3. If cached, the data is returned immediately.
4. If not cached, the API fetches data from an external source (Yahoo Finance, CoinGecko, or Steam Market) using `aiohttp`.
5. The fetched data is cached in Redis for 900 seconds and returned to the user.

The API can function without Redis, but caching significantly improves performance.

## Contributing 🤝

Want to contribute? Fork the repository, make changes, and submit a Pull Request! Future plans:
- Add Linux support for Docker.
- Expand test coverage with `pytest`.
- Integrate additional data sources.

## License 📜 


This project is licensed under the MIT License. See the [License](LICENSE) file for details.

## Contact 📫

- GitHub: [@Max2772](https://github.com/Max2772)
- Email: [bib.maxim@gmail.com](mailto:bib.maxim@gmail.com)