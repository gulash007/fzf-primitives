from typing import Callable

from ..main import Prompt
from .FzfPrompt import Result
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.options import Hotkey
from .monitoring import Logger

logger = Logger.get_logger()


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
    while True:
        try:
            prompt = prompt_builder()
            prompt.mod.on_hotkey(quit_hotkey).quit
            prompt.mod.lastly.exit_round_when_aborted()
            result_processor(prompt.run())
        except ExitRound as e:
            logger.info(f"ExitRound: {e}")
        except ExitLoop as e:
            print(f"Exiting loop: {e}")
            break
