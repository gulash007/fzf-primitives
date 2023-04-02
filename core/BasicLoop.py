from typing import Any, Callable
from .exceptions import ExitLoop, ExitRound
from .MyFzfPrompt import Result
from .Prompt import Prompt
from thingies import color


class UnexpectedResultType(Exception):
    pass


class BasicLoop:
    def __init__(self, prompt: Prompt) -> None:
        self._prompt = prompt

    def run(self):
        return self._prompt()

    def run_in_loop(self, result_processor: Callable[[Result], Any] = lambda x: None):
        while True:
            try:
                result_processor(self.run())
            except ExitRound:
                continue
            except ExitLoop as e:
                print(f"{color('Exiting loop').red.bold}: {e}")
                exit(0)
            # except Exception as e:
            #     print(f"{type(e).__name__}: {e}")
            #     return


class BasicRecursiveLoop:
    def __init__(self, starting_prompt: Prompt) -> None:
        self.starting_prompt = starting_prompt

    def run(self) -> Result:
        prompt = self.starting_prompt
        while True:
            try:
                result = prompt()
            except ExitLoop as e:
                print(f"{color('Exiting loop').red.bold}: {e}")
                exit(0)
            if isinstance(result, Result):
                return result
            elif isinstance(result, Prompt):
                prompt = result
                continue
            else:
                raise UnexpectedResultType(f"{type(result)}")
