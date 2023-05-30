from pathlib import Path
from typing import Iterable


from ..core.FzfPrompt.ActionMenu import Action
from ..core import BasePrompt, mods
from ..core.BasicLoop import BasicLoop
from ..core.FzfPrompt.constants import TOP_LEVEL_PACKAGE_PATH
from ..core.FzfPrompt.Prompt import Result
from ..core.FzfPrompt.PromptData import PromptData
from ..core.FzfPrompt.Server import ServerCall
from ..core.monitoring.Logger import LOG_FORMAT, get_logger, remove_handler

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TEST ALL KINDS OF STUFF


def hello(prompt_data):
    return "hello"


def quit(result: Result):
    raise Exception


# @mods.action.custom("Become hello", "become(printf 'hello\\nworld')", "ctrl-y")
# @mods.action.get_current_preview("ctrl-c")
@mods.on_event("ctrl-a").toggle_all
# @mods.action.toggle_all("ctrl-a").composed_with(mods.action.toggle_all("ctrl-a"))
# @mods.on_event("ctrl-c").clip
# @mods.on_event("ctrl-c")
# @mods.on_event("ctrl-c")("whatever", ServerCall())
# @mods.on_event("ctrl-c")("whatever", )
# @mods.action.clip_current_preview("ctrl-c")
# @mods.on_event("ctrl-q").post_process_action(quit)
@mods.on_event("ctrl-q").quit
@mods.preview.basic("ctrl-h")
@mods.preview.custom(name="basic2", hotkey="ctrl-y", command="echo hello", window_size="10%", window_position="up")
@mods.multiselect
# @mods.exit_round_on_no_selection("No selection!")
def run(prompt_data: PromptData):
    return BasePrompt.run(prompt_data)


if __name__ == "__main__":
    logger = get_logger()
    remove_handler("MAIN_LOG_FILE")
    remove_handler("STDERR")
    log_file_path = Path(__file__).parent.parent.joinpath("_logs/TestPrompt.log")
    logger.add(log_file_path, level="DEBUG", format=LOG_FORMAT, colorize=True)
    logger.enable("")
    logger.info("TestPrompt running…")
    print(run(PromptData(choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10])))
    # BasicLoop(lambda: run(PromptData(choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10]))).run_in_loop()
