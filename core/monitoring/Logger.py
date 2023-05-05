from __future__ import annotations

import os
import sys
from functools import partialmethod
from pathlib import Path
from typing import Literal

import loguru
from loguru import logger


__all__ = ["get_logger", "HANDLERS", "remove_handler"]

logger.remove()
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{module}</cyan> - "
    "<white>{function}</white>:"
    "<white>{line}</white>: "
    "<level>{message}</level>"
)

LOG_FILE_PATH = Path(__file__).parents[2].joinpath("_logs/main.log")


class HANDLERS:
    STDERR = logger.add(sys.stderr, level="DEBUG", format=LOG_FORMAT, colorize=True)
    MAIN_LOG_FILE = logger.add(LOG_FILE_PATH, level="DEBUG", format=LOG_FORMAT, colorize=True)


HandlerID = Literal["STDERR", "MAIN_LOG_FILE"]


def remove_handler(handler_id: HandlerID):
    logger.remove(HANDLERS.__dict__[handler_id])


logger.level("WEIRDNESS", no=42, icon="🤖", color="<MAGENTA><bold>")
logger.__class__.weirdness = partialmethod(logger.__class__.log, "WEIRDNESS")
logger.disable("")  # Disabled by default


def get_logger() -> loguru.Logger:
    return logger
