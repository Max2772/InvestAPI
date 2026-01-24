import logging
from src.env import LOG_LEVEL

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

logger = logging.getLogger(__name__)

fmt_console = "%(asctime)s - %(levelname)s - %(message)s"
fmt_warning = "%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s"

formatter = LevelFormatter(fmt_default=fmt_console, fmt_warn=fmt_warning, datefmt="%d.%m.%y %H:%M")

logger_level = getattr(logging, LOG_LEVEL, logging.INFO)

root = logging.getLogger()
root.setLevel(logger_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(logger_level)
console_handler.setFormatter(formatter)

root.addHandler(console_handler)