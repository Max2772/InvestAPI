import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL: str = (os.getenv("LOG_LEVEL") or "INFO").upper()

API_HOST: str = os.getenv("API_HOST") or "0.0.0.0"
API_PORT: int = int(os.getenv("API_PORT") or 8000)
API_RELOAD: bool = (os.getenv("API_RELOAD").upper() or "TRUE") in ("TRUE", "YES", "ON", "1")

REDIS_HOST: str = os.getenv("REDIS_HOST") or "0.0.0.0"
REDIS_PORT: int = int(os.getenv("REDIS_PORT") or 6379)
REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD") or None

REDIS_STOCK_INTERVAL: int = int(os.getenv("REDIS_STOCK_INTERVAL") or 900)
REDIS_CRYPTO_INTERVAL: int = int(os.getenv("REDIS_CRYPTO_INTERVAL") or 300)
REDIS_STEAM_INTERVAL: int = int(os.getenv("REDIS_STEAM_INTERVAL") or 900)


class LevelFormatter(logging.Formatter):
    def __init__(self, fmt_default, fmt_warn, datefmt=None):
        super().__init__(fmt=fmt_default, datefmt=datefmt)
        self.fmt_default = fmt_default
        self.fmt_warn = fmt_warn

    def format(self, record):
        if record.levelno >= logging.WARNING:
            self._style._fmt = self.fmt_warn
        else:
            self._style._fmt = self.fmt_default
        return super().format(record)


def setup_logging() -> logging.Logger:
    app_logger = logging.getLogger("investapi")

    if app_logger.handlers:
        return app_logger

    fmt_console = "%(asctime)s - %(levelname)s - %(message)s"
    fmt_warning = "%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s"
    formatter = LevelFormatter(
        fmt_default=fmt_console,
        fmt_warn=fmt_warning,
        datefmt="%d.%m.%y %H:%M",
    )

    logger_level = getattr(logging, LOG_LEVEL, logging.INFO)
    app_logger.setLevel(logger_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)

    return app_logger


logger = setup_logging()
