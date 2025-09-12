import subprocess
from typing import get_args

from fzf_primitives.core.FzfPrompt.options.actions import BaseAction, ParametrizedActionType


def test_base_actions():
    fzf_bindings = []
    for action in get_args(BaseAction):
        fzf_bindings.append(f"--bind=a:{action}")

    subprocess.check_output(["fzf", "--version", *fzf_bindings])


def test_parametrized_actions():
    fzf_bindings = []
    for action in get_args(ParametrizedActionType):
        fzf_bindings.append(f"--bind=a:{action}(0)")

    subprocess.check_output(["fzf", "--version", *fzf_bindings])


if __name__ == "__main__":
    test_base_actions()
    test_parametrized_actions()
