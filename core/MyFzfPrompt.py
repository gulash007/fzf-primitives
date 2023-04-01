import json
from typing import Iterable, Optional

from pyfzf import FzfPrompt

from .options import EMPTY_OPTS, Options

__all__ = ["run_fzf_prompt"]


class Result(list):
    """Expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey.
    This is implemented in default options for convenience.
    Also expects --print-query"""

    def __init__(self, fzf_result: list[str]) -> None:
        self.hotkey: Optional[str] = None
        self.query = ""
        if fzf_result:
            self.hotkey = fzf_result[1]
            self.query = fzf_result[0]
        super().__init__(fzf_result[2:])

    def consume(self, hotkey: str):
        if self.hotkey == hotkey:
            self.hotkey = None
            return True
        return False

    def __str__(self) -> str:
        return json.dumps({"hotkey": self.hotkey, "query": self.query, "values": self})


REQUIRED_OPTS = ["--expect=enter", "--print-query"]


class MyFzfPrompt(FzfPrompt):
    _required_options = Options(*REQUIRED_OPTS)

    def prompt(self, choices: Iterable = None, fzf_options: Options = EMPTY_OPTS, delimiter="\n") -> Result:
        return Result(super().prompt(choices, str(self._required_options + fzf_options), delimiter))


DEFAULT_FZF_PROMPT = MyFzfPrompt()
run_fzf_prompt = DEFAULT_FZF_PROMPT.prompt
