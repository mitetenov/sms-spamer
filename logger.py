"""Colored logging for the SMS bomber bot."""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Add ANSI colors to log levels."""

    COLORS = {
        logging.DEBUG: "\033[36m",     # cyan
        logging.INFO: "\033[32m",      # green
        logging.WARNING: "\033[33m",   # yellow
        logging.ERROR: "\033[31m",     # red
        logging.CRITICAL: "\033[35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up colored console logging with optional file output."""
    logger = logging.getLogger("smsbot")
    logger.setLevel(level)

    # Console handler with colors
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(
        ColoredFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                         datefmt="%H:%M:%S")
    )
    logger.addHandler(console)

    # File handler without colors
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    return logger
