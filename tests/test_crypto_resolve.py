import pytest

from app.utils import AssetNotFoundError
from app.utils.crypto_parser import resolve_crypto_coin, resolve_crypto_coins


def test_resolve_by_symbol():
    coin = resolve_crypto_coin("TON")
    assert coin.id == "the-open-network"
    assert coin.symbol == "TON"
    assert coin.full_name == "Toncoin"


def test_resolve_by_name():
    coin = resolve_crypto_coin("Toncoin")
    assert coin.id == "the-open-network"


def test_resolve_by_id():
    coin = resolve_crypto_coin("the-open-network")
    assert coin.id == "the-open-network"
    assert coin.symbol == "TON"


def test_resolve_by_symbol_sol():
    coin = resolve_crypto_coin("SOL")
    assert coin.id == "solana"
    assert coin.symbol == "SOL"
    assert coin.full_name == "Solana"


def test_resolve_unknown_slug_fallback():
    coin = resolve_crypto_coin("some-new-coin")
    assert coin.id == "some-new-coin"
    assert coin.symbol == "SOME-NEW-COIN"
    assert coin.full_name == "some-new-coin"


def test_resolve_not_found():
    with pytest.raises(AssetNotFoundError):
        resolve_crypto_coin("!!!")


def test_resolve_multiple_coins():
    coins = resolve_crypto_coins("bitcoin,ETH,Solana")
    assert [c.id for c in coins] == ["bitcoin", "ethereum", "solana"]


def test_resolve_multiple_deduplicates():
    coins = resolve_crypto_coins("solana,SOL")
    assert len(coins) == 1
    assert coins[0].id == "solana"
