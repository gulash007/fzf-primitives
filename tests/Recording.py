from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import loguru
import pydantic

from ..core.FzfPrompt import EndStatus, Result
from ..core.FzfPrompt.options import Hotkey, Situation
from ..core.monitoring import Logger

RECORDINGS_DIR = Path(__file__).parent.joinpath("recordings/")


class Event(pydantic.BaseModel):
    process: str
    thread: str
    function: str
    extra: dict


class Recording(pydantic.BaseModel):
    name: str
    events: list[Event] = []
    end_status: EndStatus = None  # type: ignore
    event: Hotkey | Situation = None  # type: ignore
    query: str = None  # type: ignore
    choices: list[str] = None  # type: ignore
    lines: list[str] = None  # type: ignore

    def __call__(self, message: loguru.Message):
        self.events.append(
            Event(
                process=message.record["process"].name,
                thread=message.record["thread"].name,
                function=message.record["function"],
                extra=message.record["extra"],
            )
        )

    def save_result(self, result: Result):
        self.end_status = result.end_status
        self.event = result.event
        self.query = result.query
        self.choices = list(map(str, result))
        self.lines = result.lines

    def compare_result(self, result: Result) -> bool:
        return (
            self.end_status == result.end_status
            and self.event == result.event
            and self.query == result.query
            and self.choices == list(map(str, result))
            and self.lines == result.lines
        )

    def compare_events(self, other: Self) -> bool:
        return self.events == other.events

    def enable_logging(self):
        logger = Logger.get_logger()
        logger.add(self, level="TRACE", filter=lambda record: record["level"].no == 5, serialize=True, enqueue=True)

    def save(self):
        path = self.get_path(self.name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, name: str):
        with open(cls.get_path(name), "r", encoding="utf8") as f:
            return cls.model_validate_json(f.read())

    @staticmethod
    def get_path(name: str) -> Path:
        return RECORDINGS_DIR.joinpath(f"{name}.json")


if __name__ == "__main__":
    print(Recording.load("TestPrompt"))
