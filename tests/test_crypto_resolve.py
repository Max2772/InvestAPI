import pytest

from app.utils import AssetNotFoundError
from app.utils.crypto_parser import resolve_crypto_coin


def test_resolve_by_symbol():
    assert resolve_crypto_coin("TON") == "the-open-network"


def test_resolve_by_name():
    assert resolve_crypto_coin("Toncoin") == "the-open-network"


def test_resolve_by_id():
    assert resolve_crypto_coin("the-open-network") == "the-open-network"


def test_resolve_by_symbol_sol():
    assert resolve_crypto_coin("SOL") == "solana"


def test_resolve_unknown_slug_fallback():
    assert resolve_crypto_coin("some-new-coin") == "some-new-coin"


def test_resolve_not_found():
    with pytest.raises(AssetNotFoundError):
        resolve_crypto_coin("!!!")
