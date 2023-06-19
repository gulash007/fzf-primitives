import pytest
from pathlib import Path
from typing import Iterable

from ..core.FzfPrompt.exceptions import ExitLoop

from . import TestPrompt
from ..core import BasePrompt, mods
from ..core.BasicLoop import BasicLoop
from ..core.FzfPrompt.constants import TOP_LEVEL_PACKAGE_PATH
from ..core.FzfPrompt.Prompt import Action, Binding, PostProcessAction, PromptData, Result, ServerCall
from ..core.monitoring import Logger

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TEST ALL KINDS OF STUFF


@mods.automate(Binding("clear query", "clear-query", "clear-query"))
@mods.automate("ctrl-a")
@mods.automate_actions("toggle-all")
@mods.automate("ctrl-q")
def run(prompt_data: PromptData):
    return TestPrompt.run(prompt_data)


def test_prompt():
    with pytest.raises(ExitLoop) as exc:
        logger = Logger.get_logger()
        Logger.remove_handler("MAIN_LOG_FILE")
        Logger.remove_handler("STDERR")
        Logger.add_file_handler("AutomatedTestPrompt", serialize=True)
        Logger.clear_log_file("AutomatedTestPrompt")
        logger.enable("")
        logger.info("AutomatedTestPrompt running…")
        pd = PromptData(choices=[x for x in HOLLY_VAULT.iterdir() if x.is_file()][:10])
        print(run(pd))


if __name__ == "__main__":
    test_prompt()
