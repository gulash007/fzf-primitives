from pathlib import Path
from typing import Iterable

from ..core import BasePrompt, mods
from ..core.BasicLoop import BasicLoop
from ..core.FzfPrompt.constants import TOP_LEVEL_PACKAGE_PATH
from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.FzfPrompt.Prompt import Action, Binding, PostProcessAction, PromptData, Result, ServerCall
from ..core.monitoring import Logger

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TEST ALL KINDS OF STUFF


def hello(prompt_data):
    return "hello"


def quit_app(prompt_data: PromptData):
    raise ExitLoop("Quitting app")


@mods.automate(Binding("clear query", "clear-query", "clear-query"))
@mods.automate("ctrl-a")
@mods.automate_actions("toggle-all")
@mods.automate("ctrl-q")
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
@mods.preview.basic("ctrl-h")
@mods.preview.custom(name="basic2", hotkey="ctrl-y", command="echo hello", window_size="50%", window_position="up")
@mods.multiselect
@mods.exit_round_when_aborted("Aborted!")
@mods.on_event("ctrl-c").clip_current_preview.run("abort", end_prompt="abort")
def run(prompt_data: PromptData):
    return BasePrompt.run(prompt_data)


if __name__ == "__main__":
    logger = Logger.get_logger()
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("TestPrompt")
    logger.enable("")
    logger.info("TestPrompt running…")
    pd = PromptData(choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10])
    print(run(pd))
    # BasicLoop(lambda: run(PromptData(choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10]))).run_in_loop()
