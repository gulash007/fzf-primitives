from __future__ import annotations

from logging import Logger
from pathlib import Path
from typing import Self

import loguru
import pydantic

from ..core.FzfPrompt.options import FzfEvent, Hotkey
from ..core.FzfPrompt.Prompt import PromptEndingAction, Result
from ..core.monitoring.Logger import get_logger

PATH = Path(__file__).parent.joinpath("recording.json")


class Event(pydantic.BaseModel):
    ...


class Recording(pydantic.BaseModel):
    events: list[Event] = []
    end_status: PromptEndingAction = None
    event: Hotkey | FzfEvent = None
    query: str = None
    selections: list[str] = None

    def __call__(self, message: loguru.Message):
        self.events.append(Event())

    def save_result(self, result: Result):
        self.end_status = result.end_status
        self.event = result.event
        self.query = result.query
        self.selections = list(result)

    def compare_result(self, result: Result) -> bool:
        return (
            self.end_status == result.end_status
            and self.event == result.event
            and self.query == result.query
            and self.selections == list(result)
        )

    def compare_events(self, other: Self) -> bool:
        return self.events == other.events

    def enable_logging(self):
        logger = get_logger()
        logger.add(self, level="TRACE", filter=lambda record: record["level"].no == 5, serialize=True, enqueue=True)
        logger.enable("")

    def save(self):
        with open(PATH, "w", encoding="utf8") as f:
            f.write(self.json(indent=2))

    @classmethod
    def load(cls):
        return pydantic.parse_file_as(cls, PATH)


if __name__ == "__main__":
    print(Recording.load())
