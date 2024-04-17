from __future__ import annotations

import pytest

from ..config import DEFAULT_ABORT_HOTKEY, DEFAULT_ACCEPT_HOTKEY
from ..core.FzfPrompt.exceptions import ExitLoop, ExitRound
from ..core.FzfPrompt.Prompt import PromptData
from ..core.monitoring import Logger
from . import TestPrompt
from .Recording import Recording

# TODO: test resolved options (need to control for variables)


# ❗ Checking events might be non-deterministic. Try running this test multiple times
def test_general():
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("AutomatedTestPrompt", level="TRACE")
    recording = Recording(name="AutomatedTestPrompt")
    recording.enable_logging()
    prompt = TestPrompt.prompt_builder()
    prompt.mod.automate_actions("up")
    prompt.mod.automate_actions("down")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate(DEFAULT_ACCEPT_HOTKEY)
    result = prompt.run()
    recording.save_result(result)
    recording.save()
    expected = Recording.load("TestPrompt")
    assert expected.end_status == result.end_status
    assert expected.event == result.event
    assert expected.query == result.query
    assert expected.lines == result.lines
    assert recording.compare_events(expected), f"{len(recording.events)=} vs {len(expected.events)=}"


def run_and_quit(prompt_data: PromptData):
    prompt = TestPrompt.prompt_builder()
    prompt.mod.automate("ctrl-q")
    return prompt.run()


def test_quit():
    with pytest.raises(ExitLoop) as exc:
        run_and_quit(PromptData())


def run_and_abort(prompt_data: PromptData):
    prompt = TestPrompt.prompt_builder()
    prompt.mod.lastly.exit_round_when_aborted()
    prompt.mod.automate(DEFAULT_ABORT_HOTKEY)
    return prompt.run()


def test_abort():
    with pytest.raises(ExitRound) as exc:
        run_and_abort(PromptData())


if __name__ == "__main__":
    test_general()
