# Black magic layer
from __future__ import annotations
import json
from typing import Literal

from pyfzf import FzfPrompt

from .PromptData import PromptData

from .options import Hotkey, Options


REQUIRED_OPTS = Options("--expect=enter", "--print-query")  # Result needs these in order to work


# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable specified in vscode-insiders://file/Users/honza/.dotfiles/.zshforfzf:4
def run_fzf_prompt(prompt_data: PromptData, delimiter="\n", *, executable_path=None) -> Result:
    # print("MyFzfPrompt:")
    # print("\n".join(prompt_data.options.options))
    print(prompt_data.options)
    # TODO: log options here: logger.info(f"Running fzf prompt with options: {options}")
    return Result(
        FzfPrompt(executable_path).prompt(prompt_data.choices, str(REQUIRED_OPTS + prompt_data.options), delimiter)
    )


# Expects --print-query so it can interpret the first element as query.
# Also expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey.
# This is implemented in required options for convenience.
class Result(list[str]):
    def __init__(self, fzf_result: list[str]) -> None:
        self.hotkey: Hotkey | Literal[""] = ""
        self.query = ""
        if fzf_result:
            self.hotkey = fzf_result[1]
            self.query = fzf_result[0]
        super().__init__(fzf_result[2:])

    def __str__(self) -> str:
        return json.dumps({"hotkey": self.hotkey, "query": self.query, "values": self})


if __name__ == "__main__":
    pass
