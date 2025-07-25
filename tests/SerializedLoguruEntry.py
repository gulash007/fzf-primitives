from __future__ import annotations

from typing import Any, TypedDict


class SerializedLoguruEntry(TypedDict):
    text: str
    record: Record


class Record(TypedDict):
    elapsed: Elapsed
    exception: Exception
    extra: dict[str, Any]
    file: File
    function: str
    level: Level
    line: int
    message: str
    module: str
    name: str
    process: ProcessOrThread
    thread: ProcessOrThread
    time: Time


class Elapsed(TypedDict):
    repr: str
    seconds: float


class Exception(TypedDict):
    type: str
    value: str
    traceback: bool


class File(TypedDict):
    name: str
    path: str


class Level(TypedDict):
    icon: str
    name: str
    no: int


class ProcessOrThread(TypedDict):
    id: int
    name: str


class Time(TypedDict):
    repr: str
    timestamp: float
