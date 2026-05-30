from __future__ import annotations

from app.schemas.search_responses import (
    CryptoSearchHit,
    SearchHit,
    SearchResponse,
    SteamSearchHit,
    StockSearchHit,
)
from app.types.constants.crypto_symbols import CRYPTO_COINS
from app.types.constants.steam_names import STEAM_NAMES
from app.types.constants.stock_tickers import STOCK_TICKERS
from app.types.enums.enums import AssetType

_PREFIX_SCORE = 100
_SUBSTRING_PRIMARY_SCORE = 60
_SUBSTRING_SECONDARY_SCORE = 40


def _match_score(query: str, primary: str, secondary: str = "") -> int | None:
    q = query.casefold()
    primary_cf = primary.casefold()
    secondary_cf = secondary.casefold()

    if primary_cf.startswith(q):
        return _PREFIX_SCORE
    if secondary_cf.startswith(q):
        return _PREFIX_SCORE - 10
    if q in primary_cf:
        return _SUBSTRING_PRIMARY_SCORE
    if secondary_cf and q in secondary_cf:
        return _SUBSTRING_SECONDARY_SCORE
    return None


def _search_stocks(query: str) -> list[tuple[int, str, StockSearchHit]]:
    ranked: list[tuple[int, str, StockSearchHit]] = []

    for ticker, full_name in STOCK_TICKERS.items():
        score = _match_score(query, ticker, full_name)
        if score is None:
            continue
        ranked.append(
            (score, ticker, StockSearchHit(name=ticker, full_name=full_name))
        )

    return ranked


def _search_crypto(query: str) -> list[tuple[int, str, CryptoSearchHit]]:
    ranked: list[tuple[int, str, CryptoSearchHit]] = []

    for coin_id, symbol, full_name in CRYPTO_COINS:
        scores = [
            score
            for score in (
                _match_score(query, symbol),
                _match_score(query, coin_id),
                _match_score(query, full_name),
            )
            if score is not None
        ]
        if not scores:
            continue
        ranked.append(
            (
                max(scores),
                symbol,
                CryptoSearchHit(
                    name=coin_id,
                    symbol=symbol,
                    full_name=full_name,
                ),
            )
        )

    return ranked


def _search_steam(query: str) -> list[tuple[int, str, SteamSearchHit]]:
    ranked: list[tuple[int, str, SteamSearchHit]] = []

    for name, (app_id, class_id) in STEAM_NAMES.items():
        score = _match_score(query, name)
        if score is None:
            continue
        ranked.append(
            (
                score,
                name.casefold(),
                SteamSearchHit(name=name, app_id=app_id, class_id=class_id),
            )
        )

    return ranked


def _take_top(
    ranked: list[tuple[int, str, SearchHit]],
    limit: int,
) -> list[SearchHit]:
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [hit for _, _, hit in ranked[:limit]]


def search_assets(
    query: str,
    asset_type: AssetType | None = None,
    limit: int = 20,
) -> SearchResponse:
    q = query.strip()
    if not q:
        return SearchResponse(query=query, results=[])

    ranked: list[tuple[int, str, SearchHit]] = []
    if asset_type in (None, AssetType.STOCK):
        ranked.extend(_search_stocks(q))
    if asset_type in (None, AssetType.CRYPTO):
        ranked.extend(_search_crypto(q))
    if asset_type in (None, AssetType.STEAM):
        ranked.extend(_search_steam(q))

    return SearchResponse(query=q, results=_take_top(ranked, limit))


async def get_asset_search(
    query: str,
    asset_type: AssetType | None = None,
    limit: int = 20,
) -> SearchResponse:
    return search_assets(query, asset_type, limit)
