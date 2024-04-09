from __future__ import annotations

import sys
from functools import partialmethod
from pathlib import Path
from typing import Literal, overload

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

LOG_FILE_FOLDER = Path(__file__).parents[2].joinpath("_logs/")


@overload
def add_file_handler(
    file_name: str,
    file_path: None = None,
    *,
    level="DEBUG",
    format=LOG_FORMAT,
    colorize=True,
    **kwargs,
): ...


@overload
def add_file_handler(
    file_name: None = None,
    file_path: str | Path = "",
    *,
    level="DEBUG",
    format=LOG_FORMAT,
    colorize=True,
    **kwargs,
): ...


def add_file_handler(
    file_name: str | None = None,
    file_path: str | Path | None = None,
    *,
    level="DEBUG",
    format=LOG_FORMAT,
    colorize=True,
    **kwargs,
):
    if not file_path and not file_name:
        raise ValueError("At least one of file_path and file_name has to be filled")
    file_path = file_path or LOG_FILE_FOLDER.joinpath(f"{file_name}.log")
    return logger.add(file_path, level=level, format=format, colorize=colorize, **kwargs)


@overload
def clear_log_file(file_name: str, file_path: None = None): ...


@overload
def clear_log_file(file_name: None = None, file_path: str | Path = ""): ...


def clear_log_file(file_name: str | None = None, file_path: str | Path | None = None):
    if not file_path and not file_name:
        raise ValueError("At least on of file_path and file_name has to be filled")
    file_path = file_path or LOG_FILE_FOLDER.joinpath(f"{file_name}.log")
    with open(file_path, "r+", encoding="utf8") as f:
        f.truncate(0)


class HANDLERS:
    STDERR = logger.add(sys.stderr, level="DEBUG", format=LOG_FORMAT, colorize=True)
    MAIN_LOG_FILE = add_file_handler("main", level="DEBUG", format=LOG_FORMAT, colorize=True)


HandlerID = Literal["STDERR", "MAIN_LOG_FILE"]


def remove_handler(handler_id: HandlerID):
    logger.remove(HANDLERS.__dict__[handler_id])


logger.level("WEIRDNESS", no=42, icon="🤖", color="<MAGENTA><bold>")
logger.__class__.weirdness = partialmethod(logger.__class__.log, "WEIRDNESS")
logger.disable("")  # Disabled by default


def get_logger() -> loguru.Logger:
    return logger
