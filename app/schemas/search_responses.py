from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from app.types.enums.enums import AssetType


class StockSearchHit(BaseModel):
    asset_type: Literal[AssetType.STOCK.value] = AssetType.STOCK.value
    name: str
    full_name: str


class CryptoSearchHit(BaseModel):
    asset_type: Literal[AssetType.CRYPTO.value] = AssetType.CRYPTO.value
    name: str
    symbol: str
    full_name: str


class SteamSearchHit(BaseModel):
    asset_type: Literal[AssetType.STEAM.value] = AssetType.STEAM.value
    name: str
    class_id: int


SearchHit = Annotated[
    Union[StockSearchHit, CryptoSearchHit, SteamSearchHit],
    Field(discriminator="asset_type"),
]


class SearchResponse(BaseModel):
    query: str
    results: list[SearchHit]
