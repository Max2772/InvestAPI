from datetime import datetime
import aiosqlite
from utils.logger import get_logger

DB_PATH = "InvestAPI.db"

logger = get_logger()

async def init_db() -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT,
                                                ) 
                ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    asset_type TEXT,
                    asset_name TEXT,
                    quantity DECIMAL,
                    buy_price DECIMAL,
                    added_at TEXT
                               ) 
                ''')
        await conn.commit()
    except aiosqlite.Error as e:
        logger.info(f"Error while initializing {DB_PATH}: {e}")

async def add_user(user_id: int, user_name: str) -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name) VALUES (?, ?)",
            (user_id, user_name))
            await conn.commit()
    except aiosqlite.Error as e:
        logger.info(f"Error while adding user {DB_PATH}: {e}")

async def delete_user(user_id: int) -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute("DELETE FROM users WHERE user_id = ?", user_id)
            await conn.commit()
    except aiosqlite.Error as e:
        logger.info(f"Error while deleting user {DB_PATH}: {e}")

async def add_asset(user_id: int, asset_type: str, asset_name: str, quantity: float, buy_price: float, added_at: str) -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute("INSERT OR IGNORE into assets (user_id, asset_type, asset_name, quantity, buy_price, added_at) VALUES(?,?,?,?,?,?)",
                                user_id, asset_type, asset_name, quantity, buy_price, added_at)
            await conn.commit()
    except aiosqlite.Error as e:
        logger.info(f"Error while adding asset {asset_name}, user {user_id} {DB_PATH}: {e}")

async def delete_asset(user_id: int, asset_type: str, asset_name: str) -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute("DELETE FROM assets WHERE user_id = ? AND asset_type = ? AND asset_name = ? AND quantity = ?",
                                user_id, asset_type, asset_name)
            await conn.commit()
    except aiosqlite.Error as e:
        logger.info(f"Error while deleting asset {asset_name}, user {user_id} {DB_PATH}: {e}")

