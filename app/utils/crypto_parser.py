from __future__ import annotations

import re
from typing import NamedTuple

from app.types.constants import CRYPTO_COINS
from app.utils.exceptions import AssetNotFoundError

_ID_LIKE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

_BY_ID: dict[str, tuple[str, str, str]] = {}
_BY_SYMBOL: dict[str, str] = {}
_BY_NAME: dict[str, str] = {}


class ResolvedCrypto(NamedTuple):
    id: str
    symbol: str
    full_name: str


def _build_indexes() -> None:
    _BY_ID.clear()
    _BY_SYMBOL.clear()
    _BY_NAME.clear()
    for coin_id, symbol, full_name in CRYPTO_COINS:
        _BY_ID[coin_id] = (coin_id, symbol, full_name)
        _BY_SYMBOL[symbol.upper()] = coin_id
        _BY_NAME[full_name] = coin_id


_build_indexes()


def _from_id(coin_id: str) -> ResolvedCrypto:
    if coin := _BY_ID.get(coin_id):
        return ResolvedCrypto(*coin)
    return ResolvedCrypto(coin_id, coin_id.upper(), coin_id)


def resolve_crypto_coin(query: str) -> ResolvedCrypto:
    q = query.strip()
    if not q:
        raise AssetNotFoundError("Cryptocurrency identifier is empty")

    if coin_id := _BY_ID.get(q.lower()):
        return ResolvedCrypto(*coin_id)
    if coin_id := _BY_SYMBOL.get(q.upper()):
        return _from_id(coin_id)
    if coin_id := _BY_NAME.get(q):
        return _from_id(coin_id)

    lowered = q.lower()
    if _ID_LIKE.match(lowered):
        return _from_id(lowered)

    raise AssetNotFoundError(f"Cryptocurrency {query} not found")


def resolve_crypto_coins(queries: str) -> list[ResolvedCrypto]:
    parts = [part.strip() for part in queries.split(",") if part.strip()]
    if not parts:
        raise AssetNotFoundError("Cryptocurrency identifier is empty")

    seen: set[str] = set()
    resolved: list[ResolvedCrypto] = []
    for part in parts:
        coin = resolve_crypto_coin(part)
        if coin.id in seen:
            continue
        seen.add(coin.id)
        resolved.append(coin)
    return resolved
