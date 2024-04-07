from typing import Callable, ParamSpec

from .monitoring import Logger
from .FzfPrompt.exceptions import ExitLoop, ExitRound

logger = Logger.get_logger()

P = ParamSpec("P")


# TODO: Rename to Executor or something
# TODO: Remove Loops and make run_in_loop and run_in_recursive_loop methods of Prompt


def run_in_loop[T](run: Callable[[], T | None], result_processor: Callable[[T], None] = lambda x: None):
    while True:
        try:
            if (result := run_once(run)) is not None:
                result_processor(result)
        except ExitRound as e:
            logger.info(f"ExitRound: {e}")


def run_once[T](run: Callable[[], T]) -> T:
    try:
        return run()
    except ExitLoop as e:
        print(f"Exiting loop: {e}")
        exit(0)
