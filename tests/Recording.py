from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Self

from fzf_primitives.config import Config
from fzf_primitives.core.monitoring import Logger
from tests.SerializedLoguruEntry import SerializedLoguruEntry

RECORDINGS_DIR = Path(__file__).parent.joinpath("recordings/")


class Recording:
    def __init__(self, name: str, log_file_path: Path) -> None:
        self.name = name
        self.log_file_path = log_file_path
        self.log_info_selected_for_comparison = self.parse_log_file(log_file_path)

    def compare(self, other: Self) -> bool:
        return self.log_info_selected_for_comparison == other.log_info_selected_for_comparison

    @staticmethod
    def parse_log_file(log_file_path: Path) -> list[Any]:
        with open(log_file_path, "r", encoding="utf8") as f:
            contents = f.read()
        log_entries = [json.loads(line) for line in contents.splitlines() if line.strip()]

        return Recording.select_info(log_entries)

    @staticmethod
    def select_info(log_entries: list[SerializedLoguruEntry]) -> list[Any]:
        selected_info = []
        for log_entry in log_entries:
            record = log_entry["record"]
            if Recording.should_include_record(record):
                selected_info.append(
                    dict(
                        process=record["process"]["name"],
                        thread=record["thread"]["name"],
                        function=record["function"],
                        extra=record["extra"],
                    )
                )
        return selected_info

    @staticmethod
    def should_include_record(record) -> bool:
        return record["level"]["name"] == "TRACE"

    @classmethod
    def load(cls, name: str):
        return cls(name, cls.get_path(name))

    @staticmethod
    def get_path(name: str) -> Path:
        return RECORDINGS_DIR.joinpath(f"{name}.log")

    @staticmethod
    def setup(name: str) -> None:
        Config.logging_enabled = True
        Logger.add_file_handler(
            Path(__file__).parent.joinpath("recordings", f"{name}.log"),
            "TRACE",
            format="default",
            serialize=True,
            mode="w",
        )


if __name__ == "__main__":
    from pprint import pprint

    pprint(Recording.load("TestPrompt").log_info_selected_for_comparison, sort_dicts=False)
