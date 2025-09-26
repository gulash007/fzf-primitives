from fzf_primitives import Prompt


def test_fzf_input():
    prompt = Prompt(entries=[1, 2, 3], converter=lambda x: f"Number: {x}")
    assert prompt._prompt_data.fzf_input() == "Number: 1\nNumber: 2\nNumber: 3\n"  # noqa: SLF001


def test_multiline_fzf_input():
    prompt = Prompt(entries=["line1\nline2", "line3\nline4"])
    assert prompt._prompt_data.fzf_input(delimiter="\0") == "line1\nline2\0line3\nline4\0"  # noqa: SLF001

    prompt.mod.options.multiselect().read0()
    prompt.mod.automate_actions("select-all")
    prompt.mod.automate(prompt.config.default_accept_hotkey)
    result = prompt.run()
    assert result.selections == ["line1\nline2", "line3\nline4"]
