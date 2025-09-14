import subprocess
from typing import get_args

from fzf_primitives.core.FzfPrompt.options.triggers import Hotkey, Event


def test_available_triggers():
    fzf_bindings = []
    for trigger in [*get_args(Hotkey), *get_args(Event)]:
        fzf_bindings.append(f"--bind={trigger}:ignore")
    subprocess.check_output(["fzf", "--version", *fzf_bindings])


if __name__ == "__main__":
    test_available_triggers()
