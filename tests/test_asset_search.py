from unittest.mock import AsyncMock

import pytest

from app.schemas import SearchResponse, StockSearchHit, CryptoSearchHit, SteamSearchHit
from app.services.asset_search import search_assets
from app.types.enums.enums import AssetType


def test_search_empty_query_returns_no_results():
    response = search_assets("   ")

    assert response.query == "   "
    assert response.results == []


def test_search_stock_by_ticker_prefix():
    response = search_assets("AAP", asset_type=AssetType.STOCK, limit=5)

    assert response.query == "AAP"
    assert response.results
    assert all(isinstance(hit, StockSearchHit) for hit in response.results)
    assert any(hit.name == "AAPL" for hit in response.results)


def test_search_crypto_by_symbol():
    response = search_assets("sol", asset_type=AssetType.CRYPTO, limit=10)

    assert response.query == "sol"
    assert any(
        isinstance(hit, CryptoSearchHit) and hit.name == "solana"
        for hit in response.results
    )


def test_search_steam_by_name_fragment():
    response = search_assets("Glove Case", asset_type=AssetType.STEAM, limit=5)

    assert response.query == "Glove Case"
    assert any(
        isinstance(hit, SteamSearchHit) and hit.name == "Glove Case"
        for hit in response.results
    )


def test_search_respects_limit_across_all_types():
    response = search_assets("a", limit=3)

    assert len(response.results) <= 3


@pytest.mark.asyncio
async def test_search_endpoint_returns_service_result(client, monkeypatch):
    expected = SearchResponse(
        query="amd",
        results=[
            StockSearchHit(
                name="AMD",
                full_name="Advanced Micro Devices, Inc. Common Stock",
            )
        ],
    )
    monkeypatch.setattr(
        "app.routers.assets.get_asset_search",
        AsyncMock(return_value=expected),
    )

    response = await client.get("/search?q=amd&type=stock")

    assert response.status_code == 200
    payload = SearchResponse.model_validate(response.json())
    assert payload.query == "amd"
    assert len(payload.results) == 1
    assert payload.results[0].name == "AMD"


@pytest.mark.asyncio
async def test_search_endpoint_validates_query_length(client):
    response = await client.get("/search?q=")

    assert response.status_code == 422
