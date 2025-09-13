from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar

from fzf_primitives.config import Config
from fzf_primitives.core.monitoring import Logger

P = ParamSpec("P")
R = TypeVar("R")


class LoggingSetup:
    def __init__(self, log_subdir: Path):
        self.__log_file_path = log_subdir / f"{datetime.now().isoformat(timespec='milliseconds')}.log"
        self.__logging_set_up = False

    def attach(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def with_logging_set_up(*args: P.args, **kwargs: P.kwargs) -> R:
            if Config.logging_enabled and not self.__logging_set_up:
                Logger.remove_preset_handlers()
                Logger.add_file_handler(self.__log_file_path, serialize=True)
                self.__logging_set_up = True
            return func(*args, **kwargs)

        return with_logging_set_up
