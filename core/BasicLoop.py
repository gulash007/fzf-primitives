from .MyFzfPrompt import Result
from .Prompt import Prompt


class UnexpectedResultType(Exception):
    pass


class BasicLoop:
    def __init__(self, starting_prompt: Prompt) -> None:
        self.starting_prompt = starting_prompt

    def run(self) -> Result:
        prompt = self.starting_prompt
        while True:
            result = prompt()
            if isinstance(result, Result):
                return result
            elif isinstance(result, Prompt):
                prompt = result
                continue
            else:
                raise UnexpectedResultType(f"{type(result)}")
