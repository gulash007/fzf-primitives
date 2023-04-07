from __future__ import annotations

import os
import sys
from functools import partialmethod
from pathlib import Path

import loguru
from lib.Helpers.MyConfigParser import CONFIG
from loguru import logger

LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{process.id}</cyan> - <cyan>{process.name}</cyan> - <white>{thread.name}</white> - <white>{function}</white>:<white>{line}</white>: <level>{extra[context]} ({extra[state]}): {message}</level>"
# LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{process.id}</cyan> - <cyan>{process.name}</cyan> - <white>{thread.name}</white> - <white>{function}</white>:<white>{line}</white>: <level>{extra[context]} ({extra[state]}): {message} - {extra}</level>"
logger.remove()
logger.add(sys.stderr, level="DEBUG", format=LOG_FORMAT, enqueue=True, colorize=True)
# logger.add(sys.stderr, level="ERROR", format=LOG_FORMAT, enqueue=True, serialize=True)
LOG_PATH = Path(f"{os.getcwd()}/_logs/Crawler.log")
logger.add(
    LOG_PATH,
    level="DEBUG",
    format=LOG_FORMAT,
    enqueue=True,
    serialize=False,
    colorize=True,
    rotation=CONFIG.get("Logger", "log file rotation"),
    retention=CONFIG.get("Logger", "log file retention"),
)

logger.level("WEIRDNESS", no=42, icon="🤖", color="<MAGENTA><bold>")
logger.__class__.weirdness = partialmethod(logger.__class__.log, "WEIRDNESS")


def get_logger(context: str) -> loguru.Logger:
    return logger.bind(context=context, state="BASE")
