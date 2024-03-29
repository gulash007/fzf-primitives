from __future__ import annotations

from pathlib import Path

import pytest

from ..core import mods
from ..core.FzfPrompt.exceptions import ExitLoop, ExitRound
from ..core.FzfPrompt.Prompt import ABORT_HOTKEY, Binding, PromptData
from ..core.monitoring import Logger
from . import TestPrompt
from .Recording import Recording

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TODO: test resolved options (need to control for variables)

@mods.automate_actions("up")
@mods.automate_actions("down")
@mods.automate("ctrl-6")
@mods.automate("ctrl-y")
@mods.automate("ctrl-h")
@mods.automate("ctrl-a")
@mods.automate("enter")
def run(prompt_data: PromptData):
    return TestPrompt.run(prompt_data)


# ❗ Checking events might be non-deterministic. Try running this test multiple times
def test_prompt():
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("AutomatedTestPrompt", level="TRACE")
    recording = Recording(name="AutomatedTestPrompt")
    recording.enable_logging()
    pd = PromptData()
    run(pd)
    recording.save_result(pd.result)
    recording.save()
    expected = Recording.load("TestPrompt")
    assert expected.end_status == pd.result.end_status
    assert expected.event == pd.result.event
    assert expected.query == pd.result.query
    assert expected.selections == list(pd.result)
    assert recording.compare_events(expected), f"{len(recording.events)=} vs {len(expected.events)=}"


@mods.automate("ctrl-q")
def run_and_quit(prompt_data: PromptData):
    return TestPrompt.run(prompt_data)


def test_quit():
    with pytest.raises(ExitLoop) as exc:
        run_and_quit(PromptData())

@mods.automate(ABORT_HOTKEY)
def run_and_abort(prompt_data: PromptData):
    return TestPrompt.run(prompt_data)

def test_abort():
    with pytest.raises(ExitRound) as exc:
        run_and_abort(PromptData())

if __name__ == "__main__":
    test_prompt()
