from __future__ import annotations

from enum import Enum, auto

import pyperclip

from .. import Prompt
from ..config import Config
from ..core.FzfPrompt import PromptData, PreviewMutationArgs
from ..core.FzfPrompt.exceptions import Quitting
from ..core.monitoring import Logger
from ..core.monitoring.constants import INTERNAL_LOG_DIR
from .Recording import Recording

# TEST ALL KINDS OF STUFF


def wait_for_input(prompt_data: PromptData[DayOfTheWeek, None]):
    input("Press Enter to continue...")


def bad_server_call_function(prompt_data: PromptData[int, str]): ...


class DayOfTheWeek(Enum):
    Monday = auto()
    Tuesday = auto()
    Wednesday = auto()
    Thursday = auto()
    Friday = auto()
    Saturday = auto()
    Sunday = auto()


monday = DayOfTheWeek["Monday"]
tuesday = DayOfTheWeek(2)

TEST_CHOICES = list(DayOfTheWeek)
TEST_PRESENTED_CHOICES = [day.name for day in TEST_CHOICES]


def clip_socket_number(prompt_data, FZF_PRIMITIVES_SOCKET_NUMBER):
    pyperclip.copy(FZF_PRIMITIVES_SOCKET_NUMBER)


def prompt_builder():
    prompt = Prompt(TEST_CHOICES, TEST_PRESENTED_CHOICES)
    prompt.mod.options.multiselect
    prompt.mod.on_situation().BACKWARD_EOF.run_function("clip socket number", clip_socket_number)
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.on_hotkey().CTRL_Q.quit
    prompt.mod.on_hotkey().CTRL_C.clip_current_preview.accept
    prompt.mod.on_hotkey().CTRL_O.clip_options
    prompt.mod.on_hotkey().CTRL_N.run_function("wait", wait_for_input)
    prompt.mod.on_hotkey().CTRL_L.view_logs_in_terminal(LOG_FILE_PATH)
    # prompt.mod.on_hotkey().CTRL_X.run_function("wait", bad_server_call_function) # uncomment to reveal error
    prompt.mod.preview("ctrl-y", label="basic").basic
    # prompt.mod.preview("ctrl-6", "50%", "up", "basic 2").custom(name="'basic 2'", output_generator="echo {}", store_output=True)

    lines_or_indices_preview = prompt.mod.preview("ctrl-6")
    lines_or_indices_preview.custom("basic", "echo {+}")
    lines_or_indices_preview.mutate_preview(
        "change to indices",
        "ctrl-x",
        lambda pd: PreviewMutationArgs(window_position="up", output_generator="echo {+n}", label="indices"),
    )
    lines_or_indices_preview.mutate_preview(
        "change to lines",
        "ctrl-z",
        lambda pd: {"window_position": "left", "output_generator": "echo {+}", "label": "lines"},
        mutate_only_when_already_focused=False,
    )
    return prompt


LOG_FILE_PATH = INTERNAL_LOG_DIR.joinpath("TestPrompt.log")

if __name__ == "__main__":
    Config.logging_enabled = True
    Logger.remove_preset_handlers()
    Logger.add_file_handler(LOG_FILE_PATH, "TRACE", format="default")
    Logger.add_file_handler(INTERNAL_LOG_DIR.joinpath("TestPrompt.stackline.log"), "DEBUG", format="stackline")
    recording = Recording(name="TestPrompt")
    recording.enable_logging()
    save_recording = False
    try:
        result = prompt_builder().run()
    except Quitting:
        pass
    else:
        recording.save_result(result)
        save_recording = True
        recording.save()
