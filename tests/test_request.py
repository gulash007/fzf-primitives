import functools
import os
from pathlib import Path

from ..core.FzfPrompt.server import Request

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
