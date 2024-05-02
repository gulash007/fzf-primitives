from .. import Prompt, PromptData
from ..config import Config
from ..core.FzfPrompt import Binding, Transformation
from ..core.FzfPrompt.previewer import Preview


def test_basic_transformation():
    def select_all(prompt_data):
        return Binding("Binding in preview change Transformation", "select-all")

    prompt = Prompt([1, 2, 3])
    prompt.mod.on_hotkey("ctrl-a").run("test", Transformation(select_all))
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.mod.options.multiselect

    result = prompt.run()
    assert list(result) == [1, 2, 3]


TEST_PREVIEW = Preview("test", lambda prompt_data: "test", window_size="20%", window_position="up")


def test_transformation_with_server_calls():
    def get_preview_change_binding(prompt_data: PromptData):
        return TEST_PREVIEW.preview_change_binding

    prompt = Prompt()
    prompt.mod.on_hotkey("ctrl-n").run("test", Transformation(get_preview_change_binding))
    prompt.mod.automate("ctrl-n")
    prompt.mod.automate(Config.default_accept_hotkey)

    prompt.run()
    assert prompt._mod._prompt_data.previewer.current_preview == TEST_PREVIEW
