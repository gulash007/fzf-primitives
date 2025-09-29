from typing import Callable

from .. import Prompt
from ..core.FzfPrompt import Result
from ..core.FzfPrompt.options import Hotkey

# TODO: Rename to Executor or something

type PromptBuilder[T, S] = Callable[[], Prompt[T, S]]
type ResultProcessor[T, S] = Callable[[Result[T, S]], None]


def run_in_loop[T, S](
    prompt_builder: PromptBuilder[T, S],
    result_processor: ResultProcessor[T, S] = lambda x: None,
    quit_hotkey: Hotkey = "ctrl-q",
):
    while True:
        prompt = prompt_builder()
        prompt.mod.on_hotkey(quit_hotkey).quit()
        result = prompt.run()
        if result.end_status == "abort":
            continue
        if result.end_status == "quit":
            print("Exiting loop...")
            break
        result_processor(result)
