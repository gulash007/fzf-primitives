from __future__ import annotations

from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

if TYPE_CHECKING:
    import loguru
from ...config import Config
from . import LazyLogger as Logger

P = ParamSpec("P")
R = TypeVar("R")


class LoggedComponent:
    # HACK: Lazy loading of Logger module
    @property
    def logger(self) -> loguru.Logger:
        return Logger.get_logger()


class LoggingSetup(LoggedComponent):
    def __init__(self, log_subdir: Path, *, force_logging: bool = False):
        super().__init__()
        self.__path = log_subdir / f"{datetime.now().isoformat(timespec='milliseconds')}.log"
        self.__logging_set_up = False
        self.handler_id: int
        self.force_logging = force_logging

    def attach(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def with_logging_set_up(*args: P.args, **kwargs: P.kwargs) -> R:
            original_logging_enabled = Config.logging_enabled
            try:
                if self.force_logging:
                    Config.logging_enabled = True
                if Config.logging_enabled and not self.__logging_set_up:
                    Logger.remove_preset_handlers()
                    # TODO: Add more customization options
                    self.handler_id = Logger.add_file_handler(self.__path, serialize=True)
                    self.__logging_set_up = True
                    try:
                        return func(*args, **kwargs)
                    finally:
                        Logger.remove(self.handler_id)
                        self.__logging_set_up = False
            finally:
                Config.logging_enabled = original_logging_enabled

            return func(*args, **kwargs)

        return with_logging_set_up

    @property
    def path(self) -> Path:
        return self.__path
