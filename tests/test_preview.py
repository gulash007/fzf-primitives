from .. import Prompt, PromptData, config
from ..core.mods.preview import FileViewer


class record_preview_name:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, prompt_data: PromptData[int, list[str]]):
        prompt_data.obj.append(self.name)
        return self.name


def test_main_preview_without_event():
    prompt = Prompt([1, 2, 3], obj=[])
    name = "Check success"
    prompt.mod.preview().custom(name, record_preview_name(name))
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()

    # Main preview invoked twice at startup - once when for event "start" and once for event "focus"
    assert prompt.obj == [name, name]


def test_no_explicit_main_preview_having_first_added_as_main():
    prompt = Prompt([1, 2, 3], obj=[])
    prompt.mod.preview("ctrl-x").custom("first", record_preview_name("first"))
    prompt.mod.preview("ctrl-y").custom("second", record_preview_name("second"))
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.obj[1:] == ["first"]


# Modding
def test_file_preview():
    prompt = Prompt([__file__])
    prompt.mod.preview().file()
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.current_preview == FileViewer().view(__file__)


def test_cyclical_preview():
    prompt = Prompt([1, 2, 3], obj=[])
    prompt.mod.preview("ctrl-y").cycle({"first": record_preview_name("first"), "second": record_preview_name("second")})
    prompt.mod.preview("ctrl-x").custom("third", record_preview_name("third"))

    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-x")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)

    prompt.run()
    assert prompt.obj[1:] == ["first", "second", "first", "third", "first"]
