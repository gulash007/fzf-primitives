from typing import Literal

import pytest

from fzf_primitives import LoggingSetup, Prompt
from fzf_primitives.actions import ParametrizedAction
from fzf_primitives.core.monitoring import INTERNAL_LOG_DIR

logging_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_on_trigger_presets")


# TODO: test with filtered list


@logging_setup.attach
def test_copy_entry_into_query():
    prompt = Prompt([1, 2, 3, 4, 5, 6, 7])

    prompt.mod.automate_actions("down", "down")
    prompt.mod.on_hotkey().CTRL_6.copy_entry_into_query()
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)

    result = prompt.run()
    assert result.current == 3
    assert result.query == "3"


@logging_setup.attach
def test_clear_query_and_focus_line():
    prompt = Prompt([1, 2, 3, 4, 5, 6, 7])

    prompt.mod.on_hotkey().NUM_3.run("3", ParametrizedAction("3", "put"))
    prompt.mod.on_hotkey().CTRL_6.clear_and_refocus()

    prompt.mod.automate("3")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)

    result = prompt.run()
    assert result.current == 3


@pytest.mark.parametrize(
    ["query", "initial_pos", "direction", "expected"],
    [
        ("", 1, "down", 12),
        ("", 2, "down", 24),
        ("2", 3, "down", 26),
        ("5", 1, "down", 35),
        ("", -1, "up", 48),
        ("2", -2, "up", 12),
        ("3", -1, "up", 36),
    ],
)
@logging_setup.attach
def test_move_by(query: str, initial_pos: int, direction: Literal["down", "up"], expected: int):
    prompt = Prompt([11, 12, 23, 24, 26, 35, 36, 48, 57])

    prompt.mod.options.multi().no_sort().query(query)
    prompt.mod.on_hotkey().CTRL_6.move_by(
        f"move {direction} to the next even number", lambda pd, n: n % 2 == 0, direction
    )
    prompt.mod.automate_actions(ParametrizedAction(str(initial_pos), "pos"))
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)
    result = prompt.run()
    assert result.current == expected


@pytest.mark.parametrize(["query", "expected"], [("", [12, 24, 36]), ("2", [12, 24])])
@logging_setup.attach
def test_select_by(query: str, expected: list[int]):
    prompt = Prompt([11, 12, 23, 24, 35, 36, 47])

    prompt.mod.options.multi().no_sort().query(query)
    prompt.mod.on_hotkey().CTRL_6.select_by("select even numbers", lambda pd, n: n % 2 == 0)
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)
    result = prompt.run()
    assert result.selections == expected


@pytest.mark.parametrize(["query", "expected"], [("", [11, 23, 35, 47]), ("2", [23])])
@logging_setup.attach
def test_deselect_by(query: str, expected: list[int]):
    prompt = Prompt([11, 12, 23, 24, 35, 36, 47])

    prompt.mod.options.multi().no_sort().query(query)
    prompt.mod.on_hotkey().CTRL_6.select_by("deselect even numbers", lambda pd, n: n % 2 == 0, action="deselect")
    prompt.mod.automate_actions("select-all")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)
    result = prompt.run()
    assert result.selections == expected


@pytest.mark.parametrize(["query", "expected"], [("", [11, 23, 35, 47, 12, 24, 36]), ("2", [23, 12, 24])])
@logging_setup.attach
def test_toggle_by(query: str, expected: list[int]):
    prompt = get_toggle_by_prompt()
    prompt.mod.options.query(query)
    prompt.mod.automate_actions("select-all")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)
    result = prompt.run()
    assert result.selections == expected, f"Got: {result.selections}"


def get_toggle_by_prompt():
    prompt = Prompt([11, 12, 23, 24, 35, 36, 47])

    prompt.mod.options.multi().no_sort()
    prompt.mod.on_hotkey().CTRL_6.select_by("toggle even numbers", lambda pd, n: n % 2 == 0, action="toggle")
    return prompt


if __name__ == "__main__":
    # test_clear_query_and_focus_line()
    get_toggle_by_prompt().run()
