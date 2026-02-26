"""
Centralized application logger.
"""

import logging
import sys

from app.core.config import get_settings

settings = get_settings()


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    return logger
