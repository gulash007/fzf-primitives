from __future__ import annotations

import argparse
import contextlib
import sys
from datetime import datetime
from time import perf_counter

start = perf_counter()


from enum import Enum, auto

import pyperclip

from fzf_primitives import Prompt
from fzf_primitives.actions import ParametrizedAction
from fzf_primitives.config import Config
from fzf_primitives.core.FzfPrompt import PreviewMutationArgs, PromptData
from fzf_primitives.core.FzfPrompt.action_menu import Binding, ShellCommand
from fzf_primitives.core.FzfPrompt.exceptions import PromptEnd
from fzf_primitives.core.FzfPrompt.previewer.Preview import ChangePreviewLabel
from fzf_primitives.core.mods.vector_generator import VectorGenerator
from fzf_primitives.core.monitoring import Logger
from fzf_primitives.core.monitoring.constants import INTERNAL_LOG_DIR
from tests.Recording import Recording

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


def clip_socket_number(prompt_data, FZF_PRIMITIVES_SOCKET_NUMBER):
    pyperclip.copy(FZF_PRIMITIVES_SOCKET_NUMBER)


def prompt_builder():
    prompt = Prompt(TEST_CHOICES, lambda day: day.name)
    prompt.mod.options.multiselect.listen()
    prompt.mod.on_event().BACKWARD_EOF.run_function("clip socket number", clip_socket_number)
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.on_hotkey().CTRL_Q.quit
    prompt.mod.on_hotkey().CTRL_C.clip_current_preview.accept
    prompt.mod.on_hotkey().CTRL_O.clip_options
    prompt.mod.on_hotkey().CTRL_N.run_function("wait", wait_for_input)
    prompt.mod.on_hotkey().CTRL_ALT_N.run_function("wait", lambda pd: input("Press Enter to continue..."))
    prompt.mod.on_hotkey().CTRL_L.view_logs_in_terminal(LOG_FILE_PATH)
    # prompt.mod.on_hotkey().CTRL_X.run_function("wait", bad_server_call_function) # uncomment to reveal error
    prompt.mod.preview("ctrl-y").fzf_json
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

    preview_mutation_generator = VectorGenerator(mutation_dict, get_mutation_args)
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

    prompt.mod.on_event(on_conflict="append").START.run_function(
        "measure startup time", lambda pd: print(f"Startup time: {perf_counter() - start} seconds")
    )

    prompt.mod.on_hotkey().CTRL_ALT_H.show_bindings_help_in_preview
    return prompt


LOG_FILE_PATH = INTERNAL_LOG_DIR.joinpath(f"TestPrompt/{datetime.now().isoformat(timespec='milliseconds')}.log")

if __name__ == "__main__":
    args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true", help="Enable recording")
    parsed_args = parser.parse_args(args)

    Config.logging_enabled = True
    Logger.remove_preset_handlers()
    Logger.add_file_handler(LOG_FILE_PATH, "DEBUG", serialize=True)
    if parsed_args.record:
        Recording.setup("TestPrompt")
    with contextlib.suppress(PromptEnd):
        result = prompt_builder().run()
