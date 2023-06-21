from typing import Any, Callable

from .monitoring import Logger
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.Prompt import Result
from thingies import color

logger = Logger.get_logger()


class UnexpectedResultType(Exception):
    pass


# TODO: Remove Loops and make run_in_loop and run_in_recursive_loop methods of Prompt
class BasicLoop:
    def __init__(self, run: Callable) -> None:
        self.run = run

    def run_in_loop(self, result_processor: Callable[[Result], Any] = lambda x: None):
        while True:
            try:
                result_processor(self.run())
            except ExitRound:
                continue
            except ExitLoop as e:
                logger.info(f"{color('Exiting loop').red.bold}: {e}")
                exit(0)
            # except Exception as e:
            #     print(f"{type(e).__name__}: {e}")
            #     return
