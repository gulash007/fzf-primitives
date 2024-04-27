from typing import Any

from .. import Preview, Prompt, PromptData, config
from ..core.mods.preview import FileViewer
from ..core.monitoring import Logger

logger = Logger.get_logger()


class record_preview_name:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, prompt_data: PromptData[Any, list[str]]):
        prompt_data.obj.append(self.name)
        return self.name


def test_main_preview_without_event():
    prompt = Prompt(obj=[])
    name = "Check success"
    prompt.mod.preview().custom(name, record_preview_name(name))
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()

    # Main preview invoked twice at startup - once when for event "start" and once for event "focus"
    assert prompt.obj == [name, name]


def test_no_explicit_main_preview_having_first_added_as_main():
    prompt = Prompt(obj=[])
    prompt.mod.preview("ctrl-x").custom("first", record_preview_name("first"))
    prompt.mod.preview("ctrl-y").custom("second", record_preview_name("second"))
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.obj[1:] == ["first"]


def test_storing_preview_output():
    prompt = Prompt(obj="")
    command = "printf 'hello\\nworld'"
    prompt.mod.preview().custom("first", command)

    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.current_preview == "hello\nworld"


# Modding
def get_file_preview_prompt():
    prompt = Prompt([__file__], obj=[])
    prompt.mod.preview().file()
    return prompt


def test_file_preview():
    prompt = get_file_preview_prompt()
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)
    prompt.run()
    assert prompt.current_preview == FileViewer().view(__file__)


def get_cycle_preview_functions_prompt():
    prompt = Prompt(obj=[])
    prompt.mod.preview("ctrl-y").cycle_functions(
        {"first": record_preview_name("first"), "second": record_preview_name("second")}
    )
    prompt.mod.preview("ctrl-x").custom("third", record_preview_name("third"))
    return prompt


def test_cycle_preview_functions():
    prompt = get_cycle_preview_functions_prompt()

    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-x")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)

    prompt.run()
    assert prompt.obj[1:] == ["first", "second", "first", "third", "first"]


def get_cycle_previews_prompt():
    prompt = Prompt(obj=[])
    prompt.mod.preview("ctrl-x").custom("third", record_preview_name("third"))
    prompt.mod.preview("ctrl-y").cycle_previews(
        [
            Preview("first", record_preview_name("first")),
            Preview("second", record_preview_name("second"), window_size="10%", window_position="up"),
        ]
    )
    return prompt


def test_cycle_previews():
    prompt = get_cycle_previews_prompt()

    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-x")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate(config.DEFAULT_ACCEPT_HOTKEY)

    prompt.run()
    assert prompt.obj[1:] == ["third", "first", "second", "third", "second"]


if __name__ == "__main__":
    Logger.remove_handler("STDERR")
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.add_file_handler("TraceLog", None, level="TRACE")
    logger.enable("")
    get_cycle_previews_prompt().run()
