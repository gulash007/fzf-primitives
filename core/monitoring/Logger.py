from __future__ import annotations

import os
import sys
from functools import partialmethod
from pathlib import Path

import loguru
from loguru import logger

__all__ = ["get_logger"]

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{module}</cyan> - "
    "<white>{function}</white>:"
    "<white>{line}</white>: "
    "<level>{message}</level>"
)

logger.remove()
logger.add(sys.stderr, level="DEBUG", format=LOG_FORMAT, colorize=True)

logger.level("WEIRDNESS", no=42, icon="🤖", color="<MAGENTA><bold>")
logger.__class__.weirdness = partialmethod(logger.__class__.log, "WEIRDNESS")
logger.disable("")  # Disabled by default


def get_logger() -> loguru.Logger:
    return logger
