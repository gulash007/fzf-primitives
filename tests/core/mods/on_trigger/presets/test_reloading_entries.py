import pytest

from fzf_primitives import Prompt, PromptData
from fzf_primitives.actions import MovePointer, ParametrizedAction
from fzf_primitives.config import Config
from fzf_primitives.core.FzfPrompt.action_menu.parametrized_actions import SelectAt
from fzf_primitives.core.monitoring import INTERNAL_LOG_DIR
from tests.LoggingSetup import LoggingSetup

logging_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_reloading_entries")


def add_number(prompt_data: PromptData):
    return prompt_data.entries + [prompt_data.entries[-1] + 1]


@logging_setup.attach
def test_reloading_entries():
    prompt = get_prompt_for_reloading_entries()

    prompt.mod.automate("ctrl-r")
    prompt.mod.automate("ctrl-r")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate_actions(MovePointer(4))
    prompt.mod.automate(Config.default_accept_hotkey)

    result = prompt.run()
    assert list(result) == [0, 1, 2, 3, 4, 5]
    assert result.current == 4


@logging_setup.attach
def get_prompt_for_reloading_entries():
    prompt = Prompt([0, 1, 2, 3])
    prompt.mod.on_hotkey().CTRL_R.reload_entries(add_number)
    prompt.mod.on_hotkey().CTRL_A.toggle_all()
    prompt.mod.options.multi()
    return prompt


INITIAL_PEOPLE = [{"name": "Alice", "id": 0}, {"name": "Bob", "id": 1}, {"name": "Charlie", "id": 2}]


@pytest.mark.parametrize("query", ["", "Alice", "Bob", "Nobody"])
@logging_setup.attach
def test_remembering_selections_after_reload(query):
    prompt = get_prompt_for_remembering_selections_after_reload()
    prompt.mod.automate_actions(SelectAt(1))
    prompt.mod.automate_actions(SelectAt(2))
    prompt.mod.automate_actions(ParametrizedAction(query, "put"))
    prompt.mod.automate("ctrl-x")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate_actions("clear-query")
    prompt.mod.automate(Config.default_accept_hotkey)

    result = prompt.run()
    assert result.obj["indices_before"] == result.obj["indices_after"]


@logging_setup.attach
def get_prompt_for_remembering_selections_after_reload():
    prompt = Prompt(INITIAL_PEOPLE, obj={})
    prompt.mod.on_hotkey().CTRL_X.run_function(
        "record selections before reload", lambda pd: pd.obj.update({"indices_before": pd.selected_indices.copy()})
    )
    prompt.mod.on_hotkey().CTRL_6.reload_entries(
        lambda pd: INITIAL_PEOPLE
        + [
            {"name": "David", "id": 3},
            {"name": "Person with missing id"},  # should produce error in getting key
        ],
        preserve_selections_by_key=lambda x: x["id"],
    )
    prompt.mod.on_hotkey().CTRL_Y.run_function(
        "record selections after reload", lambda pd: pd.obj.update({"indices_after": pd.selected_indices.copy()})
    )
    prompt.mod.options.multi()
    return prompt


@pytest.mark.parametrize("delimiter", ["\n", "\0"])
@logging_setup.attach
def test_reloading_entries_with_various_delimiters(delimiter):
    prompt = Prompt([0, 1, 2, 3])
    prompt.mod.on_hotkey().CTRL_6.reload_entries(lambda pd: [0, 1, 2, 3, 4])
    prompt.mod.options.multi()
    if delimiter == "\0":
        prompt.mod.options.read0()
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate_actions("select-all")
    prompt.mod.automate(prompt.config.default_accept_hotkey)
    result = prompt.run()
    assert list(result) == [0, 1, 2, 3, 4]


if __name__ == "__main__":
    get_prompt_for_reloading_entries().run()
    get_prompt_for_remembering_selections_after_reload().run()
