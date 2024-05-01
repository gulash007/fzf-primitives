from __future__ import annotations

from typing import TYPE_CHECKING

from . import LazyLogger as Logger

if TYPE_CHECKING:
    import loguru

__all__ = ["LoggedComponent", "Logger"]


class LoggedComponent:
    # HACK: Lazy loading of Logger module
    @property
    def logger(self) -> loguru.Logger:
        return Logger.get_logger()
