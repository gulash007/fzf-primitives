from typing import TYPE_CHECKING
from . import LazyLogger as Logger

if TYPE_CHECKING:
    import loguru


class LoggedComponent:
    def __init__(self):
        # HACK: Lazy loading of Logger module
        self.logger: loguru.Logger = Logger.get_logger()  # type: ignore
