from typing import Callable

from .. import Prompt
from ..core.FzfPrompt import Result
from ..core.FzfPrompt.exceptions import Quitting, Aborted
from ..core.FzfPrompt.options import Hotkey
from ..core.monitoring import Logger


# TODO: Rename to Executor or something

type PromptBuilder[T, S] = Callable[[], Prompt[T, S]]
type ResultProcessor[T] = Callable[[Result[T]], None]


def run_in_loop[
    T, S
](
    prompt_builder: PromptBuilder[T, S],
    result_processor: ResultProcessor[T] = lambda x: None,
    quit_hotkey: Hotkey = "ctrl-q",
):
    logger = Logger.get_logger()
    while True:
        try:
            prompt = prompt_builder()
            prompt.mod.on_hotkey(quit_hotkey).quit
            prompt.mod.lastly.raise_from_aborted_status()
            result_processor(prompt.run())
        except Aborted as e:
            logger.info(f"ExitRound: {e}")
        except Quitting as e:
            print(f"Exiting loop: {e}")
            break
