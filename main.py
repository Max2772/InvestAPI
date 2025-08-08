import asyncio
import logging
import sys
from src import handlers # NoQa
from src.common import bot, dp

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())