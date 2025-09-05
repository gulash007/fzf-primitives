from fzf_primitives import Prompt, PromptData
from fzf_primitives.config import Config
from fzf_primitives.core.FzfPrompt import Transform
from fzf_primitives.core.FzfPrompt.previewer import Preview


def test_basic_transform():
    prompt = Prompt([1, 2, 3])
    prompt.mod.on_hotkey("ctrl-a").run("test", Transform(lambda pd: ["select-all"]))
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.mod.options.multiselect

    result = prompt.run()
    assert list(result) == [1, 2, 3]


TEST_PREVIEW = Preview("test", output_generator=lambda prompt_data: "test", window_size="20%", window_position="up")


def test_transform_with_server_calls():
    def get_preview_change_actions(prompt_data: PromptData):
        return TEST_PREVIEW.preview_change_binding.actions

    prompt = Prompt()
    prompt.mod.on_hotkey("ctrl-n").run("test", Transform(get_preview_change_actions))
    prompt.mod.automate("ctrl-n")
    prompt.mod.automate(Config.default_accept_hotkey)

    prompt.run()
    assert prompt._prompt_data.previewer.current_preview == TEST_PREVIEW
