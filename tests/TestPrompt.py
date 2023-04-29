from pathlib import Path
from typing import Iterable

from ..core.FzfPrompt.Prompt import Result

from ..core import mods
from ..core.FzfPrompt.PromptData import PromptData
from ..core import BasePrompt
from ..core.monitoring.Logger import get_logger

# from ..core.DefaultActionMenu import DefaultActionMenu

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TEST ALL KINDS OF STUFF


# @mods.hotkey("ctrl-g", "become(echo hello)") # TODO
# @mods.preview.basic
@mods.preview.basic("ctrl-b")  # TODO
@mods.preview.custom(id="basic2", hotkey="ctrl-y", command="echo hello")
@mods.multiselect
@mods.exit_round_on_no_selection("No selection!")
def run(prompt_data: PromptData):
    return BasePrompt.run(prompt_data)


if __name__ == "__main__":
    logger = get_logger()
    logger.enable("")
    logger.info("TestPrompt running…")
    run(
        PromptData(
            choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10],
            # action_menu=DefaultActionMenu() # TODO
        )
    )
