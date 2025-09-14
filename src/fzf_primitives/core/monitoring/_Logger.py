from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

import loguru
from loguru import logger
from loguru._handler import Handler

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


HandlerName = Literal["STDERR", "MAIN_LOG_FILE", "SERIALIZED_MAIN_LOG_FILE"]

PRESET_HANDLERS: dict[HandlerName, int] = {
    "STDERR": logger.add(sys.stderr, level="DEBUG", format=LOG_FORMATS["default"], colorize=True),
    "MAIN_LOG_FILE": add_file_handler(MAIN_LOG_FILE_PATH, "DEBUG", format="default", colorize=True),
}

logger.level("WEIRDNESS", no=42, icon="🤖", color="<MAGENTA><bold>")


def remove_preset_handlers(*handler_names: HandlerName):
    for handler_name in handler_names or list(PRESET_HANDLERS.copy().keys()):
        if handler_name not in PRESET_HANDLERS:
            continue
        logger.remove(PRESET_HANDLERS[handler_name])
        PRESET_HANDLERS.pop(handler_name, None)


def remove(handler_id: int | None = None) -> None:
    logger.remove(handler_id)


def handlers() -> dict[int, Handler]:
    return getattr(logger, "_core").handlers


def get_logger() -> loguru.Logger:
    return logger
