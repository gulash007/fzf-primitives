import json

from pyfzf import FzfPrompt

from core.options import Options


class Result:
    """Expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey.
    This is implemented in default options for convenience."""

    def __init__(self, fzf_result: list[str]) -> None:
        self.hotkey = fzf_result[0] if fzf_result else None
        self.values = fzf_result[1:]

    def consume(self, hotkey: str):
        if self.hotkey == hotkey:
            self.hotkey = None
            return True
        return False

    def __str__(self) -> str:
        return json.dumps(self.__dict__)


class MyFzfPrompt(FzfPrompt):
    def prompt(self, choices=None, fzf_options: Options = Options(), delimiter="\n") -> Result:
        return Result(super().prompt(choices, str(Options().defaults + fzf_options), delimiter))


DEFAULT_FZF_PROMPT = MyFzfPrompt()
run_fzf_prompt = DEFAULT_FZF_PROMPT.prompt
