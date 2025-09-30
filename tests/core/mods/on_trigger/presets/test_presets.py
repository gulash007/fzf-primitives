import pytest

from fzf_primitives import Prompt
from fzf_primitives.actions import ParametrizedAction
from fzf_primitives.core.monitoring import INTERNAL_LOG_DIR
from tests.LoggingSetup import LoggingSetup

logging_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_on_trigger_presets")


# TODO: test with filtered list


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
