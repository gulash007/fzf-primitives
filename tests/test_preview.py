from typing import Any

from fzf_primitives import Prompt, PromptData
from fzf_primitives.config import Config
from fzf_primitives.core.FzfPrompt.previewer import Preview
from fzf_primitives.core.FzfPrompt.server import CommandOutput
from fzf_primitives.core.mods.preview_mod import FileViewer
from fzf_primitives.core.monitoring import Logger
from fzf_primitives.core.monitoring.constants import INTERNAL_LOG_DIR


class record_preview_name:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, prompt_data: PromptData[Any, list[str]]):
        prompt_data.obj.append(self.name)
        return self.name

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"


def test_main_preview_without_event():
    prompt = Prompt(obj=[])
    name = "Check success"
    prompt.mod.preview().custom(name, record_preview_name(name))
    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.run()

    assert prompt.obj == [name]


def test_no_explicit_main_preview_having_first_added_as_main():
    prompt = Prompt(obj=[])
    prompt.mod.preview("ctrl-x").custom("first", record_preview_name("first"))
    prompt.mod.preview("ctrl-y").custom("second", record_preview_name("second"))
    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.run()
    assert prompt.obj == ["first"]


def test_preview_with_preview_function_that_has_command_output():
    prompt = Prompt(obj="")
    command = "printf 'hello\\nworld'"

    def preview_function_with_command_output(prompt_data: PromptData, command_output: str = CommandOutput(command)):
        return command_output

    prompt.mod.preview().custom("first", preview_function_with_command_output)

    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.run()
    assert prompt.current_preview == "hello\nworld"


def test_storing_preview_output():
    prompt = Prompt(obj="")
    command = "printf 'hello\\nworld'"
    prompt.mod.preview().custom("first", command)

    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.run()
    assert prompt.current_preview == "hello\nworld"


# Modding
def get_file_preview_prompt():
    prompt = Prompt([__file__], obj=[])
    prompt.mod.preview().file()
    return prompt


def test_file_preview():
    prompt = get_file_preview_prompt()
    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.run()
    assert prompt.current_preview == FileViewer().view(__file__)


def get_cycle_previews_prompt():
    prompt = Prompt(obj=[])
    prompt.mod.preview("ctrl-y").cycle_previews(
        [
            Preview("first", output_generator=record_preview_name("first")),
            Preview("second", output_generator=record_preview_name("second"), window_size="10%", window_position="up"),
        ]
    )
    prompt.mod.preview("ctrl-x").custom("third", record_preview_name("third"))
    return prompt


def test_cycle_previews():
    prompt = get_cycle_previews_prompt()

    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-x")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate(Config.default_accept_hotkey)

    prompt.run()
    assert prompt.obj == ["first", "second", "first", "third", "first", "second"]


def get_cycle_mutators_prompt():
    prompt = Prompt(obj=[])
    prompt.mod.preview("ctrl-x").custom("third", record_preview_name("third"))
    prompt.mod.preview().custom("").on_hotkey().CTRL_Y.cycle_mutators(
        "",
        [
            lambda pd: {"output_generator": record_preview_name("first")},
            lambda pd: {
                "output_generator": record_preview_name("second"),
                "window_size": "10%",
                "window_position": "up",
            },
        ],
    )
    return prompt


def test_cycle_mutators():
    prompt = get_cycle_mutators_prompt()

    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-x")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate(Config.default_accept_hotkey)

    prompt.run()
    assert prompt.obj == ["third", "first", "second", "third", "second"]


LOG_FILE_PATH = INTERNAL_LOG_DIR.joinpath("test_preview.log")
if __name__ == "__main__":
    Config.logging_enabled = True
    logger = Logger.get_logger()
    Logger.remove_preset_handlers()
    Logger.add_file_handler(LOG_FILE_PATH, "TRACE")
    prompt = get_cycle_previews_prompt()
    prompt.mod.on_hotkey().CTRL_L.view_logs_in_terminal(LOG_FILE_PATH)
