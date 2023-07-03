from typing import Callable, ParamSpec, TypeVar

from .monitoring import Logger
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.Prompt import Result

logger = Logger.get_logger()

P = ParamSpec("P")
R = TypeVar("R", bound=Result | None)


# TODO: Rename to Executor or something
# TODO: Remove Loops and make run_in_loop and run_in_recursive_loop methods of Prompt


def run_in_loop(run: Callable[[], R], result_processor: Callable[[Result], None] = lambda x: None):
    while True:
        try:
            if (result := run_once(run)) is not None:
                result_processor(result)
        except ExitRound as e:
            logger.info(f"ExitRound: {e}")


def run_once(run: Callable[[], R]) -> R:
    try:
        return run()
    except ExitLoop as e:
        print(f"Exiting loop: {e}")
        exit(0)
