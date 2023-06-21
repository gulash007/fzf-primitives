from pathlib import Path
from typing import Iterable

from ..core import BasePrompt, mods
from ..core.BasicLoop import BasicLoop
from ..core.FzfPrompt.constants import TOP_LEVEL_PACKAGE_PATH
from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.FzfPrompt.Prompt import Action, Binding, PostProcessAction, PromptData, Result, ServerCall
from ..core.monitoring import Logger
from .Recording import Recording

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TEST ALL KINDS OF STUFF


def hello(prompt_data):
    return "hello"


def quit_app(prompt_data: PromptData):
    raise ExitLoop("Quitting app")


def quit_app_without_saving_recording(prompt_data: PromptData):
    raise ExitLoop("Don't save recording")


# @mods.action.custom("Become hello", "become(printf 'hello\\nworld')", "ctrl-y")
# @mods.action.get_current_preview("ctrl-c")
@mods.on_event("ctrl-a").toggle_all
# @mods.action.toggle_all("ctrl-a").composed_with(mods.action.toggle_all("ctrl-a"))
# @mods.on_event("ctrl-c").clip
# @mods.on_event("ctrl-c")
# @mods.on_event("ctrl-c").run("whatever", ServerCall())
# @mods.on_event("ctrl-c").run("whatever", )
# @mods.action.clip_current_preview("ctrl-c")
@mods.on_event("ctrl-q").run("quit", PostProcessAction(quit_app), end_prompt="abort")
# @mods.on_event("ctrl-q").quit
@mods.on_event("ctrl-alt-q").run(
    "quit without saving recording", PostProcessAction(quit_app_without_saving_recording), end_prompt="abort"
)
@mods.preview.basic("ctrl-h")
@mods.preview.custom(name="basic2", hotkey="ctrl-y", command="echo hello", window_size="50%", window_position="up")
@mods.multiselect
@mods.exit_round_when_aborted("Aborted!")
@mods.on_event("ctrl-c").clip_current_preview.run("abort", end_prompt="abort")
def run(prompt_data: PromptData):
    prompt_data.choices = [x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10]
    return BasePrompt.run(prompt_data)


if __name__ == "__main__":
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("TestPrompt", level="TRACE")
    recording = Recording(name="TestPrompt")
    recording.enable_logging()
    pd = PromptData()
    save_recording = True
    try:
        run(pd)
    except ExitLoop as e:
        if str(e) == "Don't save recording":
            save_recording = False
    recording.save_result(pd.result)
    if save_recording:
        recording.save()
    # BasicLoop(lambda: run(PromptData(choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10]))).run_in_loop()
