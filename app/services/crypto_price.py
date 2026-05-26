from datetime import datetime

import aiohttp

from app.config import CRYPTO_PROVIDER_NAME, REDIS_CRYPTO_INTERVAL
from app.database import RedisClient
from app.schemas import CryptoPricesResponse, CryptoResponse
from app.utils import AssetNotFoundError, handle_error_exception
from app.utils.crypto_parser import ResolvedCrypto, resolve_crypto_coins
from app.utils.logging import logger


def _build_crypto_response(coin: ResolvedCrypto, price: int | float) -> CryptoResponse:
    return CryptoResponse(
        name=coin.id,
        symbol=coin.symbol,
        full_name=coin.full_name,
        price=round(price, 2),
        currency="USD",
        cached_at=datetime.now(),
    )


async def _fetch_crypto_prices(
    coins: list[ResolvedCrypto],
    http_session: aiohttp.ClientSession,
) -> dict[str, CryptoResponse]:
    ids = ",".join(coin.id for coin in coins)
    logger.info(
        f"Fetching coin data for {len(coins)} assets from {CRYPTO_PROVIDER_NAME}"
    )
    url = (
        "https://api.coingecko.com/api/v3/simple/"
        f"price?ids={ids}&vs_currencies=usd"
    )

    async with http_session.get(url) as response:
        data = await response.json()
        response.raise_for_status()

    results: dict[str, CryptoResponse] = {}
    missing: list[str] = []

    for coin in coins:
        coin_data = data.get(coin.id)
        if not coin_data or "usd" not in coin_data:
            missing.append(coin.id)
            continue

        price = coin_data.get("usd")
        if price is None or not isinstance(price, (int, float)):
            missing.append(coin.id)
            continue

        results[coin.id] = _build_crypto_response(coin, price)

    if missing:
        raise AssetNotFoundError(
            f"Price not available for cryptocurrencies: {', '.join(missing)}"
        )

    return results


async def get_crypto_prices(
    coins: str,
    redis_client: RedisClient | None,
    http_session: aiohttp.ClientSession,
) -> CryptoPricesResponse:
    resolved = resolve_crypto_coins(coins)

    cached: dict[str, CryptoResponse] = {}
    to_fetch: list[ResolvedCrypto] = []

    if redis_client:
        for coin in resolved:
            cache_key = f"coin:{coin.id}"
            cache = await redis_client.get_cache(cache_key, CryptoResponse)
            if cache:
                cached[coin.id] = cache
            else:
                to_fetch.append(coin)
    else:
        to_fetch = resolved

    try:
        if to_fetch:
            fetched = await _fetch_crypto_prices(to_fetch, http_session)
            if redis_client:
                for coin_id, response_data in fetched.items():
                    await redis_client.set_cache(
                        f"coin:{coin_id}",
                        response_data,
                        REDIS_CRYPTO_INTERVAL,
                    )
            cached.update(fetched)

        ordered = [cached[coin.id] for coin in resolved]
        return CryptoPricesResponse(coins=ordered)
    except AssetNotFoundError:
        raise
    except Exception as e:
        coin_ids = ", ".join(coin.id for coin in resolved)
        logger.error(f"Error fetching crypto [{coin_ids}]: {e}")
        raise handle_error_exception(e, source=CRYPTO_PROVIDER_NAME) from e
