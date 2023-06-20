from __future__ import annotations

from pathlib import Path

import pytest

from ..core import mods
from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.FzfPrompt.Prompt import Binding, PromptData
from ..core.monitoring import Logger
from . import TestPrompt
from .Recording import Recording

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")


@mods.automate("ctrl-y")
@mods.automate("ctrl-h")
@mods.automate("ctrl-a")
@mods.automate("enter")
def run(prompt_data: PromptData):
    return TestPrompt.run(prompt_data)


def test_prompt():
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    recording = Recording()
    recording.enable_logging()
    pd = PromptData()
    run(pd)
    recording.save_result(pd.result)

    expected = Recording.load()
    assert expected.end_status == pd.result.end_status
    assert expected.event == pd.result.event
    assert expected.query == pd.result.query
    assert expected.selections == list(pd.result)
    assert recording.compare_events(expected), f"{len(recording.events)=} vs {len(expected.events)=}"


@mods.automate("ctrl-q")
def run_and_exit(prompt_data: PromptData):
    return TestPrompt.run(prompt_data)


def test_exit():
    with pytest.raises(ExitLoop) as exc:
        run_and_exit(PromptData())


if __name__ == "__main__":
    test_prompt()
