from __future__ import annotations

from time import perf_counter

start = perf_counter()


from enum import Enum, auto

import pyperclip

from .. import Prompt
from ..actions import ParametrizedAction
from ..config import Config
from ..core.FzfPrompt import PreviewMutationArgs, PromptData
from ..core.FzfPrompt.action_menu import Binding, ShellCommand
from ..core.FzfPrompt.exceptions import Quitting
from ..core.FzfPrompt.previewer.Preview import ChangePreviewLabel
from ..core.mods.multi_dimensional_generator import MultiDimensionalGenerator
from ..core.monitoring import Logger
from ..core.monitoring.constants import INTERNAL_LOG_DIR
from .Recording import Recording

print(f"Imports: {perf_counter() - start} seconds")
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
    prompt.mod.on_hotkey().CTRL_ALT_N.run_function("wait", lambda pd: input("Press Enter to continue..."))
    prompt.mod.on_hotkey().CTRL_L.view_logs_in_terminal(LOG_FILE_PATH)
    # prompt.mod.on_hotkey().CTRL_X.run_function("wait", bad_server_call_function) # uncomment to reveal error
    prompt.mod.preview("ctrl-y").fzf_json
    # prompt.mod.preview("ctrl-6", "50%", "up", "basic 2").custom(name="'basic 2'", output_generator="echo {}", store_output=True)
    mutation_dict = {
        "is hello": [False, True],
        "has world": [True, False],
    }

    def get_mutation_args(is_hello, has_world) -> PreviewMutationArgs:
        return PreviewMutationArgs(
            output_generator=f"echo {'Hello' if is_hello else 'Bye'}{' World' if has_world else ''}",
            window_position="right" if is_hello else "left",
            label="world" if has_world else "",
        )

    preview_mutation_generator = MultiDimensionalGenerator(mutation_dict, get_mutation_args)
    complex_preview = prompt.mod.preview("ctrl-6").custom("Hello World")
    complex_preview.on_hotkey().CTRL_X.mutate(
        "[Hello World] Cycle between hello right/bye left",
        lambda pd: preview_mutation_generator.next("is hello"),
        auto_apply_first=True,
    )
    complex_preview.on_hotkey().CTRL_Z.mutate(
        "[Hello World] Cycle between world/no world",
        lambda pd: preview_mutation_generator.next("has world"),
    )

    prompt.mod.on_hotkey().CTRL_B.run_shell_command("First", "echo -n First && read")
    prompt.mod.on_hotkey(on_conflict="cycle with").CTRL_B.run_shell_command("Second", "echo -n Second && read")
    prompt.mod.on_hotkey(on_conflict="cycle with").CTRL_B.run_shell_command("Third", "echo -n Third && read")

    prompt.mod.on_situation(on_conflict="append").START.run_function(
        "measure startup time", lambda pd: print(f"Startup time: {perf_counter() - start} seconds")
    )

    prompt.mod.on_hotkey().CTRL_ALT_H.show_bindings_help_in_preview
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
