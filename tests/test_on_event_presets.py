from fzf_primitives import Prompt
from fzf_primitives.actions import ParametrizedAction


def test_clear_query_and_focus_line():
    prompt = Prompt([1, 2, 3, 4, 5, 6, 7])

    prompt.mod.on_hotkey().NUM_3.run("3", ParametrizedAction("3", "put"))
    prompt.mod.on_hotkey().CTRL_6.clear_and_refocus

    prompt.mod.automate("3")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate(Prompt.config.default_accept_hotkey)

    result = prompt.run()
    assert result.current == 3

if __name__ == "__main__":
    test_clear_query_and_focus_line()