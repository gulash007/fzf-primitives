import functools
import os
import re
from pathlib import Path

import pytest

from fzf_primitives import Prompt, PromptData
from fzf_primitives.core.FzfPrompt import Binding
from fzf_primitives.core.FzfPrompt.server import CommandOutput, ReusedServerCall, ServerCall, ServerEndpoint
from fzf_primitives.core.FzfPrompt.server.actions import PromptEndingAction

CORRECT_COMMAND_PATH = Path(__file__).parent.joinpath("test_request/correct_command.txt")
CREATED_COMMAND_PATH = Path(__file__).parent.joinpath("test_request/created_command.txt")
COMMAND_CREATION_TEST_ENDPOINT = ServerEndpoint(lambda pd: None, "ID with 'quotes'", "ctrl-n")


def test_create_command():
    with open(CORRECT_COMMAND_PATH, "r", encoding="utf-8") as f:
        expected_command = f.read()
    create_command = ServerCall._create_command  # noqa: SLF001
    created_command = create_command(COMMAND_CREATION_TEST_ENDPOINT.id, COMMAND_CREATION_TEST_ENDPOINT.function)
    Path(os.path.dirname(CREATED_COMMAND_PATH)).mkdir(parents=True, exist_ok=True)
    with open(CREATED_COMMAND_PATH, "w", encoding="utf-8") as f:
        f.write(created_command)

    assert created_command == expected_command


def test_handling_lambdas():
    lambda_function = lambda prompt_data, p1, p2: None
    params = ServerCall._parse_function_parameters(lambda_function)  # noqa: SLF001
    assert [p.name for p in params] == ["p1", "p2"]


def test_handling_decorated_functions():
    def func(prompt_data, p1, p2): ...

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    params = ServerCall._parse_function_parameters(decorator(func))  # noqa: SLF001
    assert [p.name for p in params] == ["p1", "p2"]


def test_handling_partial_functions():
    def func(prompt_data, p1, p2): ...

    params = ServerCall._parse_function_parameters(functools.partial(func, p2="arg2"))  # noqa: SLF001
    assert [p.name for p in params] == ["p1"]


def test_server_call():
    prompt = Prompt(obj=[])
    prompt_data = prompt._prompt_data  # noqa: SLF001
    prompt_data.action_menu.add(
        "start",
        Binding(
            "Add 1",
            ServerCall(lambda pd: pd.obj.append(1), "description with '\"nested quotes\"'"),
            PromptEndingAction("accept"),
        ),
    )  # noqa: SLF001
    prompt.run()
    assert prompt.obj[0] == 1


@pytest.mark.parametrize(
    "command, expected",
    [
        ("printf 'hello\\nworld'", "hello\nworld"),
        ("printf 'a \"quote\" inside quotes'", 'a "quote" inside quotes'),
        ('printf "nested $(printf "quotes") inside"', "nested quotes inside"),
        ("this_command_does_not_exist", ".*command not found.*"),  # errors should be passed as output
    ],
    ids=[
        "normal command",
        "command with nested quotes",
        "command with command substitution",
        "nonexistent command",
    ],
)
def test_ending_prompt_with_command_output(command: str, expected: str):
    prompt = Prompt(obj="")

    def function_with_command_output(prompt_data: PromptData, command_output: str = CommandOutput(command)):
        prompt_data.obj = command_output

    prompt_data = prompt._prompt_data  # noqa: SLF001
    prompt_data.action_menu.add(  # noqa: SLF001
        "start", Binding("Hello world", ServerCall(function_with_command_output), PromptEndingAction("accept"))
    )
    prompt.run()
    assert re.match(expected, prompt.obj), f"'{prompt.obj}' doesn't match pattern '{expected}'"


def test_the_same_server_call_with_multiple_times():
    prompt = Prompt(use_basic_hotkeys=False)
    reused_server_call = ServerCall(lambda pd: None)
    prompt_data = prompt._prompt_data  # noqa: SLF001
    prompt_data.action_menu.add("ctrl-a", Binding("Added", reused_server_call))  # noqa: SLF001
    prompt_data.action_menu.add("ctrl-b", Binding("Reused", reused_server_call))  # noqa: SLF001
    with pytest.raises(ReusedServerCall):
        prompt._run_initial_setup()  # noqa: SLF001
