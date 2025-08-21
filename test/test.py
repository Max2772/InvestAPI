import asyncio
from src.investapi import get_stock_price, get_crypto_price, get_steam_item_price, CRYPTO_SYMBOLS


async def main():
    stock = await get_stock_price('AMD')
    print(f"get_stock_price:\n{stock}\n")

    crypto = await get_crypto_price('BTC')
    print(f"get_crypto_price:\n{crypto}\n")

    steam = await get_steam_item_price(730, 'Glove Case')
    print(f"get_steam_item_price:\n{steam}\n")

    if 'BTC' in CRYPTO_SYMBOLS:
        print(True)

    if 'BCC' not in CRYPTO_SYMBOLS:
        print(False)

if __name__ == '__main__':
    asyncio.run(main())