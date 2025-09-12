import subprocess
from typing import get_args

from fzf_primitives.core.FzfPrompt.options.events import Hotkey, Situation


def test_available_events():
    fzf_bindings = []
    for event in [*get_args(Hotkey), *get_args(Situation)]:
        fzf_bindings.append(f"--bind={event}:ignore")
    subprocess.check_output(["fzf", "--version", *fzf_bindings])


if __name__ == "__main__":
    test_available_events()
