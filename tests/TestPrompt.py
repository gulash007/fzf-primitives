from __future__ import annotations

from enum import Enum, auto

from .. import Prompt
from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.FzfPrompt.prompt_data import PromptData
from ..core.monitoring import Logger
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


def prompt_builder():
    prompt = Prompt(TEST_CHOICES, TEST_PRESENTED_CHOICES)
    prompt.mod.options.multiselect
    prompt.mod.on_situation().BACKWARD_EOF.run_shell_command("clip socket number", "echo $SOCKET_NUMBER | clip")
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.on_hotkey().CTRL_Q.quit
    prompt.mod.on_hotkey().CTRL_C.clip_current_preview.accept
    prompt.mod.on_hotkey().CTRL_O.clip_options
    prompt.mod.on_hotkey().CTRL_N.run_function("wait", wait_for_input)
    # prompt.mod.on_hotkey().CTRL_X.run_function("wait", bad_server_call_function) # uncomment to reveal error
    prompt.mod.preview("ctrl-y", label="basic").basic
    prompt.mod.preview("ctrl-6", "50%", "up", "basic 2").custom(name="'basic 2'", command="echo {}", store_output=True)
    return prompt


if __name__ == "__main__":
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("TestPrompt", level="TRACE")
    recording = Recording(name="TestPrompt")
    recording.enable_logging()
    save_recording = False
    try:
        result = prompt_builder().run()
    except ExitLoop:
        pass
    else:
        recording.save_result(result)
        save_recording = True
        recording.save()
