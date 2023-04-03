from __future__ import annotations
import json
from typing import Iterable, Optional

from pyfzf import FzfPrompt

from .options import Options


REQUIRED_OPTS = Options("--expect=enter", "--print-query")  # Result needs these in order to work


def run_fzf_prompt(
    choices: Iterable = None, options: Options = Options(), delimiter="\n", *, executable_path=None
) -> Result:
    return Result(FzfPrompt(executable_path).prompt(choices, str(REQUIRED_OPTS + options), delimiter))


class Result(list):
    """Expects --print-query so it can interpret the first element as query.
    Also expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey.
    This is implemented in required options for convenience.
    """

    def __init__(self, fzf_result: list[str]) -> None:
        self.hotkey: Optional[str] = None
        self.query = ""
        if fzf_result:
            self.hotkey = fzf_result[1]
            self.query = fzf_result[0]
        super().__init__(fzf_result[2:])

    def __str__(self) -> str:
        return json.dumps({"hotkey": self.hotkey, "query": self.query, "values": self})


if __name__ == "__main__":
    pass
