from __future__ import annotations

import re

from app.types.constants import CRYPTO_COINS
from app.utils.exceptions import AssetNotFoundError


_BY_ID: dict[str, str] = {}
_BY_SYMBOL: dict[str, str] = {}
_BY_NAME: dict[str, str] = {}

_ID_LIKE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


def _norm_name(value: str) -> str:
    return "-".join(value.lower().split())


def _build_indexes() -> None:
    _BY_ID.clear()
    _BY_SYMBOL.clear()
    _BY_NAME.clear()
    for coin_id, symbol, name in CRYPTO_COINS:
        _BY_ID[coin_id] = coin_id
        _BY_SYMBOL[symbol.upper()] = coin_id
        key = _norm_name(name)
        if key not in _BY_NAME:
            _BY_NAME[key] = coin_id


_build_indexes()


def resolve_crypto_coin(query: str) -> str:
    q = query.strip()
    if not q:
        raise AssetNotFoundError("Cryptocurrency identifier is empty")

    if coin_id := _BY_ID.get(q.lower()):
        return coin_id
    if coin_id := _BY_SYMBOL.get(q.upper()):
        return coin_id
    if coin_id := _BY_NAME.get(_norm_name(q)):
        return coin_id

    lowered = q.lower()
    if _ID_LIKE.match(lowered):
        return lowered

    raise AssetNotFoundError(f"Cryptocurrency {query} not found")
