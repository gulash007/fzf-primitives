from __future__ import annotations

from typing import TYPE_CHECKING

from . import LazyLogger as Logger
from .constants import INTERNAL_LOG_DIR

if TYPE_CHECKING:
    import loguru

__all__ = ["LoggedComponent", "Logger", "INTERNAL_LOG_DIR"]


class LoggedComponent:
    # HACK: Lazy loading of Logger module
    @property
    def logger(self) -> loguru.Logger:
        return Logger.get_logger()
