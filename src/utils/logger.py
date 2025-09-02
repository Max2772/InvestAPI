from typing import Optional
import logging
from logging.handlers import RotatingFileHandler

LOG_LEVEL_MAPPING = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "FATAL": logging.CRITICAL,
    "CRITICAL": logging.CRITICAL,
}

_logger = None

def setup_logger(log_level: Optional[str] = None) -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    log_level = LOG_LEVEL_MAPPING.get(log_level, logging.INFO)

    _logger = logging.getLogger(__name__)
    _logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    if log_level == logging.INFO:
        console_handler.setFormatter(logging.Formatter('%(asctime)s - [%(processName)-11s] %(levelname)s - %(message)s'))
    else:
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - [%(processName)-11s] %(levelname)s - '
                              '%(module)s.%(funcName)s:%(lineno)d - %(message)s'))
    _logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        'logs.log', maxBytes=2*1024*1024, backupCount=3, encoding="utf-8", errors="replace"
    )
    file_handler.setLevel(log_level)

    if log_level == logging.INFO:
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(processName)-11s] %(message)s'))
    else:
        file_handler.setFormatter(logging.Formatter('%(asctime)s - [%(processName)-11s] %(levelname)s - '
                                                    '%(module)s.%(funcName)s:%(lineno)d - %(message)s'))

    _logger.addHandler(file_handler)
    _logger.info("Loger initialized")

    return _logger

def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        temp_logger = logging.getLogger(__name__)
        return temp_logger

    return _logger