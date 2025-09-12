from fzf_primitives import Prompt, PromptData
from fzf_primitives.config import Config


def double_entries(prompt_data: PromptData):
    return prompt_data.entries + [prompt_data.entries[-1] + 1]


def test_reloading_entries():
    prompt = Prompt([1, 2, 3])
    prompt.mod.on_hotkey().CTRL_R.reload_entries(double_entries)
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.options.multiselect

    prompt.mod.automate("ctrl-r")
    prompt.mod.automate("ctrl-r")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate_actions("pos(4)")  # type: ignore
    prompt.mod.automate(Config.default_accept_hotkey)

    result = prompt.run()
    assert list(result) == [1, 2, 3, 4, 5]
    assert result.current == 4


if __name__ == "__main__":
    test_reloading_entries()
