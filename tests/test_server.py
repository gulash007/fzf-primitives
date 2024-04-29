import functools
import os
from pathlib import Path

import pytest

from .. import Prompt, PromptData
from ..core.FzfPrompt.server import Request, CommandOutput
import re

CORRECT_COMMAND_PATH = Path(__file__).parent.joinpath("test_request/correct_command.txt")
CREATED_COMMAND_PATH = Path(__file__).parent.joinpath("test_request/created_command.txt")
COMMAND_CREATION_TEST_ARGS = ("ID with 'quotes'", lambda pd: None, "execute")


def test_create_command():
    with open(CORRECT_COMMAND_PATH, "r", encoding="utf-8") as f:
        expected_command = f.read()

    created_command = Request.create_command(*COMMAND_CREATION_TEST_ARGS)
    Path(os.path.dirname(CREATED_COMMAND_PATH)).mkdir(parents=True, exist_ok=True)
    with open(CREATED_COMMAND_PATH, "w", encoding="utf-8") as f:
        f.write(created_command)

    assert created_command == expected_command


def test_handling_partial_functions():
    def func(prompt_data, p1, p2): ...

    params = Request.parse_function_parameters(functools.partial(func, p2="arg2"))
    assert [p.name for p in params] == ["p1"]


def test_server_call():
    prompt = Prompt(obj=[])
    prompt.mod.on_situation("start").run_function("Add 1", lambda pd: pd.obj.append(1)).accept
    prompt.run()
    assert prompt.obj[0] == 1


@pytest.mark.parametrize(
    "command, expected",
    [
        ("printf 'hello\\nworld'", "hello\nworld"),
        ("this_command_does_not_exist", ".*command not found.*"),  # errors should be passed as output
    ],
)
def test_server_call_with_command_output(command: str, expected: str):
    prompt = Prompt(obj="")

    def function_with_command_output(prompt_data: PromptData, command_output: str = CommandOutput(command)):
        prompt_data.obj = command_output

    prompt.mod.on_situation("start").run_function("Hello world", function_with_command_output).accept
    prompt.run()
    assert re.match(expected, prompt.obj), f"'{prompt.obj}' doesn't match pattern '{expected}'"
