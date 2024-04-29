from .. import Prompt, PromptData
from ..config import Config


def double_choices(prompt_data: PromptData):
    return (new_choices := [2 * x for x in prompt_data.choices]), [str(x) for x in new_choices]


def test_reloading_choices():
    prompt = Prompt([1, 2, 3])
    prompt.mod.on_hotkey().CTRL_R.reload_choices(double_choices)
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.options.multiselect

    prompt.mod.automate("ctrl-r")
    prompt.mod.automate("ctrl-r")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate(Config.default_accept_hotkey)

    result = prompt.run()
    assert list(result) == [4, 8, 12]
    assert result.lines == ["4", "8", "12"]


if __name__ == "__main__":
    test_reloading_choices()
