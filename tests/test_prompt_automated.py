from __future__ import annotations
from datetime import datetime

import pytest

from ..config import Config
from ..core.FzfPrompt.exceptions import Aborted, Quitting
from ..core.monitoring import Logger
from ..core.monitoring.constants import INTERNAL_LOG_DIR
from . import TestPrompt
from .Recording import Recording

# TODO: test resolved options (need to control for variables)


# ❗ Checking events might be non-deterministic. Try running this test multiple times
def test_general():
    Config.logging_enabled = True
    Logger.remove_preset_handlers()
    LOG_FILE_PATH = INTERNAL_LOG_DIR.joinpath(
        f"TestPromptAutomated/{datetime.now().isoformat(timespec='milliseconds')}.log"
    )
    Logger.add_file_handler(LOG_FILE_PATH, serialize=True)

    Recording.setup("TestPromptAutomated")

    prompt = TestPrompt.prompt_builder()
    prompt.mod.automate_actions("up")
    prompt.mod.automate_actions("down")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate(Config.default_accept_hotkey)
    prompt.run()

    recording = Recording.load("TestPromptAutomated")
    expected = Recording.load("TestPrompt")
    assert expected.compare(recording)


def test_quit():
    with pytest.raises(Quitting):
        prompt = TestPrompt.prompt_builder()
        prompt.mod.automate("ctrl-q")
        prompt.run()


def test_abort():
    with pytest.raises(Aborted):
        prompt = TestPrompt.prompt_builder()
        prompt.mod.lastly.raise_from_aborted_status()
        prompt.mod.automate(Config.default_abort_hotkey)
        prompt.run()


if __name__ == "__main__":
    test_general()
