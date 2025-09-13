from __future__ import annotations

from enum import Enum, auto

import pytest

from fzf_primitives.config import Config
from fzf_primitives.core import Prompt
from fzf_primitives.core.FzfPrompt.exceptions import Aborted, Quitting
from fzf_primitives.core.monitoring.constants import INTERNAL_LOG_DIR
from tests.LoggingSetup import LoggingSetup
from tests.Recording import Recording

# TODO: test resolved options (need to control for variables)


logging_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_prompt_automated")


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


@logging_setup.attach
def prompt_builder():
    prompt = Prompt(TEST_CHOICES, lambda day: day.name)
    prompt.mod.options.multiselect.listen()
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.on_hotkey().CTRL_Q.quit
    prompt.mod.preview("ctrl-y").fzf_json
    prompt.mod.preview("ctrl-6").custom("Hello World")

    return prompt


# ❗ Checking events might be non-deterministic. Try running this test multiple times
@logging_setup.attach
def test_general():
    Recording.setup("TestPromptAutomated")

    prompt = prompt_builder()
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


@logging_setup.attach
def test_quit():
    with pytest.raises(Quitting):
        prompt = prompt_builder()
        prompt.mod.automate("ctrl-q")
        prompt.run()


@logging_setup.attach
def test_abort():
    with pytest.raises(Aborted):
        prompt = prompt_builder()
        prompt.mod.lastly.raise_from_aborted_status()
        prompt.mod.automate(Config.default_abort_hotkey)
        prompt.run()


if __name__ == "__main__":
    test_general()
