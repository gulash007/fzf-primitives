from typing import Callable, ParamSpec

from ..main import Prompt
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.Prompt import Result
from .monitoring import Logger

logger = Logger.get_logger()

P = ParamSpec("P")


# TODO: Rename to Executor or something

type PromptBuilder[T, S] = Callable[[], Prompt[T, S]]
type ResultProcessor[T] = Callable[[Result[T]], None]


def run_in_loop[T, S](prompt_builder: PromptBuilder[T, S], result_processor: ResultProcessor[T] = lambda x: None):
    while True:
        try:
            prompt = prompt_builder()
            prompt.mod.on_event("ctrl-q").quit
            prompt.mod.lastly.exit_round_when_aborted()
            result_processor(prompt.run())
        except ExitRound as e:
            logger.info(f"ExitRound: {e}")
        except ExitLoop as e:
            print(f"Exiting loop: {e}")
            break
