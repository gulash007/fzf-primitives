from __future__ import annotations
import traceback
from typing import TYPE_CHECKING, Literal
from pathlib import Path

if TYPE_CHECKING:
    from loguru import FormatFunction, Record


LogFormat = Literal["default", "stackline"]


def stackline(record: Record) -> str:
    record["message"]
    record["extra"].update(
        stack_line=".".join(f"{Path(frame.filename).stem}.{frame.name}" for frame in traceback.extract_stack()[:-3])
    )
    assert isinstance(LOG_FORMATS["default"], str)
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>| "
        "<level>{level: <8}</level>| "
        "<cyan>{extra[stack_line]}</cyan>: "
        "<level>{message}</level>"
        "\n"
    )


LOG_FORMATS: dict[LogFormat, str | FormatFunction] = {
    "default": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>| "
        "<level>{level: <8}</level>| "
        "<cyan>{module}</cyan> - "
        "<white>{function}</white>:"
        "<white>{line}</white>: "
        "<level>{message}</level>"
    ),
    "stackline": stackline,
}

INTERNAL_LOG_DIR = Path(__file__).parents[4].joinpath("_logs/").absolute()
MAIN_LOG_FILE_PATH = INTERNAL_LOG_DIR.joinpath("main.log")
SERIALIZED_MAIN_LOG_FILE_PATH = INTERNAL_LOG_DIR.joinpath("main_serialized.log")
