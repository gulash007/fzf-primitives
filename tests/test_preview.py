from .. import Prompt, PromptData, config


class record_preview_name:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, prompt_data: PromptData[int, str]):
        prompt_data.obj = self.name
        return "Preview function ran successfully"


def test_main_preview_without_event():
    prompt = Prompt([1, 2, 3], obj="")
    name = "Check success"
    prompt.mod.preview().custom(name, record_preview_name(name))
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.obj == name


def test_no_explicit_main_preview_having_first_added_as_main():
    prompt = Prompt([1, 2, 3], obj="")
    prompt.mod.preview("ctrl-x").custom("first", record_preview_name("first"))
    prompt.mod.preview("ctrl-y").custom("second", record_preview_name("second"))
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.obj == "first"
