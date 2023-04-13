from __future__ import annotations
import json
from typing import Iterable, Optional

from pyfzf import FzfPrompt

from .options import Options


REQUIRED_OPTS = Options("--expect=enter", "--print-query")  # Result needs these in order to work


# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable specified in vscode-insiders://file/Users/honza/.dotfiles/.zshforfzf:4
def run_fzf_prompt(
    choices: Iterable | None = None, options: Options = Options(), delimiter="\n", *, executable_path=None
) -> Result:
    choices = choices or []
    # TODO: log options here: logger.info(f"Running fzf prompt with options: {options}")
    return Result(FzfPrompt(executable_path).prompt(choices, str(REQUIRED_OPTS + options), delimiter))


# Expects --print-query so it can interpret the first element as query.
# Also expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey.
# This is implemented in required options for convenience.
class Result(list[str]):
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
