# Black magic layer
from __future__ import annotations

import json
import subprocess
import tempfile
import threading
from pathlib import Path
from shutil import which
from typing import Literal

from ..monitoring.Logger import get_logger
from .ActionMenu import Action, PostProcessAction, ShellCommand
from .options import Hotkey, Options
from .PromptData import PromptData
from .Server import Server

logger = get_logger()
ACCEPT_HOTKEY: Hotkey = "enter"

FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Unbind some default fzf hotkeys (add bind 'hk:ignore' options from left)
# TODO: Solve other expected hotkeys
# TODO: Use tempfile
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable specified in vscode-insiders://file/Users/honza/.dotfiles/.zshforfzf:4
def run_fzf_prompt(prompt_data: PromptData, delimiter="\n", *, executable_path=None) -> Result:
    if not which("fzf") and not executable_path:
        raise SystemError(f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")
    else:
        executable_path = "fzf"

    fzf_result = []
    with tempfile.NamedTemporaryFile(delete=True) as output_file:
        output_file_path = Path(output_file.name)
        # TODO: generalize to solve other expected hotkeys
        prompt_data.action_menu.add("accept", ACCEPT_HOTKEY, PostProcessAction(lambda result: result))
        for hotkey, binding in prompt_data.action_menu.bindings.items():
            # TODO: what if other actions use "accept"?
            for action in binding.actions[:-1]:
                if isinstance(action, PostProcessAction):
                    raise RuntimeError("PostProcessAction has to come last")
            if isinstance(binding.actions[-1], PostProcessAction):
                binding.actions[-1:] = [
                    ShellCommand(f"arr=({{q}} {hotkey} {{+}}) && printf '%s\\n' \"${{arr[@]}}\" > {output_file_path}"),
                    "accept",
                ]

        server_setup_finished = threading.Event()
        server = Server(prompt_data, server_setup_finished, daemon=True)
        server.start()
        server_setup_finished.wait()

        options = prompt_data.resolve_options()
        logger.debug("\n".join(options.options))

        # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
        # TODO: 🧊 Use subprocess.run without shell=True (need to change Options)
        try:
            subprocess.run(
                f"{executable_path} {options}",
                shell=True,
                input=delimiter.join(str(choice) for choice in prompt_data.choices).encode(),
                check=True,
            )
            fzf_result = output_file_path.read_text("utf-8").splitlines()
        except subprocess.CalledProcessError as err:
            if err.returncode != 130:  # 130 means aborted
                raise

    return prompt_data.action_menu.process_result(Result(fzf_result))
    # result = Result(FzfPrompt(executable_path).prompt(prompt_data.choices, str(options), delimiter))
    # return prompt_data.action_menu.process_result(result)


# Expects --print-query so it can interpret the first element as query.
# Also expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey.
# This is implemented in required options for convenience.
# TODO: Adapt result to change in getting selections (current result is historical and cryptic)
class Result(list[str]):
    def __init__(self, fzf_result: list[str]) -> None:
        self.hotkey: Hotkey | Literal[""] = ""
        self.query = ""
        logger.info(fzf_result)
        if fzf_result:
            self.hotkey = fzf_result[1]
            self.query = fzf_result[0]
        super().__init__(fzf_result[2:])

    def __str__(self) -> str:
        return json.dumps({"hotkey": self.hotkey, "query": self.query, "values": self})


if __name__ == "__main__":
    pass
