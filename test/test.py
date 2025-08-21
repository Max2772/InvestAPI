import asyncio
from investapi import CRYPTO_SYMBOLS, InvestAPI

api = InvestAPI(redis=True)

async def main():
    stock_price = await api.stock('AMD')
    print(f"get_stock_price:\n{stock_price}\n")

    crypto_price = await api.crypto('BTC')
    print(f"get_crypto_price:\n{crypto_price}\n")

    steam_price = await api.steam(730, 'Glove Case')
    print(f"get_steam_item_price:\n{steam_price}\n")

    if 'BTC' in CRYPTO_SYMBOLS:
        print(True)

    if 'BCC' not in CRYPTO_SYMBOLS:
        print(False)

if __name__ == '__main__':
    asyncio.run(main())