from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

import loguru
from loguru import logger

from .constants import LOG_FORMATS, MAIN_LOG_FILE_PATH, LogFormat

__all__ = ["get_logger", "remove_preset_handlers", "add_file_handler"]


logger.remove()


LogLevel = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


def add_file_handler(
    file_path: Path | str,
    level: LogLevel = "DEBUG",
    format: LogFormat = "default",
    colorize: bool = True,
    **kwargs,
):
    return logger.add(file_path, level=level, format=LOG_FORMATS[format], colorize=colorize, **kwargs)


HandlerID = Literal["STDERR", "MAIN_LOG_FILE"]

PRESET_HANDLERS: dict[HandlerID, int] = {
    "STDERR": logger.add(sys.stderr, level="DEBUG", format=LOG_FORMATS["default"], colorize=True),
    "MAIN_LOG_FILE": add_file_handler(MAIN_LOG_FILE_PATH, "DEBUG", format="default", colorize=True),
}


def remove_preset_handlers(*handler_ids: HandlerID):
    if not handler_ids:
        for handler_number in PRESET_HANDLERS.values():
            logger.remove(handler_number)
    for handler_id in handler_ids:
        logger.remove(PRESET_HANDLERS[handler_id])


def get_logger() -> loguru.Logger:
    return logger
