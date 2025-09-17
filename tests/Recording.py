from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import loguru

from fzf_primitives.config import Config
from fzf_primitives.core.monitoring import Logger

RECORDINGS_DIR = Path(__file__).parent.joinpath("recordings/")


class Recording:
    def __init__(self, name: str, log_file_path: Path) -> None:
        self.name = name
        self.log_file_path = log_file_path
        self.text = self.parse_log_file(log_file_path)

    @staticmethod
    def parse_log_file(log_file_path: Path) -> str:
        with open(log_file_path, "r", encoding="utf8") as f:
            return f.read()

    @classmethod
    def load(cls, name: str):
        return cls(name, cls.get_path(name))

    @staticmethod
    def get_path(name: str) -> Path:
        return RECORDINGS_DIR.joinpath(f"{name}.log")

    @staticmethod
    def setup(name: str) -> None:
        Config.logging_enabled = True
        path = Path(__file__).parent.joinpath("recordings", f"{name}.log")

        def filter_loguru(record: loguru.Record) -> bool:
            return (
                "automator" not in (record["name"] or "")
                and record["extra"].get("trace_point") != "resolving_server_call"
                and "_move_to_next_binding" not in record["message"]
            )

        fmt = "{level}|{process.name}|{thread.name}|{name}.{function}|{extra[trace_point]}"
        Logger.get_logger().add(path, level="TRACE", format=fmt, filter=filter_loguru, mode="w")


if __name__ == "__main__":
    print(Recording.load("expected").text)
