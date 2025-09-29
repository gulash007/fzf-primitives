from __future__ import annotations

import functools
from dataclasses import dataclass, field
from enum import Enum, auto

import pytest

from fzf_primitives.config import Config
from fzf_primitives.core import Prompt
from fzf_primitives.core.mods.preview_mod.presets import get_fzf_json, preview_basic
from fzf_primitives.core.monitoring.constants import INTERNAL_LOG_DIR
from tests.LoggingSetup import LoggingSetup

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


@dataclass
class Recording:
    selections: list[DayOfTheWeek] = field(default_factory=list)
    previews: list[str] = field(default_factory=list)


n = 0


def hello_world(prompt_data):
    global n
    n += 1
    return f"{n}: Hello World"


EXPECTED_RECORDING = Recording(
    selections=TEST_CHOICES,
    # cursor movement and changing selections refreshes preview (unless done simultaneously, then it just counts as one)
    previews=[
        *[preview_basic.__name__] * 3,
        get_fzf_json.__name__,
        *[hello_world.__name__] * 7,
    ],
)


def show_and_record_preview(preview_function):
    @functools.wraps(preview_function)
    def wrapper(prompt_data, *args, **kwargs):
        prompt_data.obj.previews.append(preview_function.__name__)
        return preview_function(prompt_data, *args, **kwargs)

    return wrapper


@logging_setup.attach
def prompt_builder():
    prompt = Prompt(TEST_CHOICES, lambda day: day.name, obj=Recording())
    prompt.mod.options.multi().listen()
    prompt.mod.on_hotkey().CTRL_A.toggle_all()
    prompt.mod.on_hotkey().CTRL_N.run_function(
        "record selections", lambda pd: pd.obj.selections.extend(pd.selections), silent=True
    )
    prompt.mod.on_hotkey().TAB.run("select next", "down", "select")
    prompt.mod.on_hotkey().CTRL_Q.quit()
    prompt.mod.preview().custom("basic", show_and_record_preview(preview_basic))
    prompt.mod.preview("ctrl-y").custom("fzf json", show_and_record_preview(get_fzf_json))
    prompt.mod.preview("ctrl-6").custom("Hello World", show_and_record_preview(hello_world))

    return prompt


@logging_setup.attach
def test_general():
    prompt = prompt_builder()
    prompt.mod.automate_actions("up")
    prompt.mod.automate_actions("down")
    prompt.mod.automate("ctrl-y")
    prompt.mod.automate("ctrl-6")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate("ctrl-n")
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate("tab", "tab", "tab")
    prompt.mod.automate_actions("down")
    prompt.mod.automate(Config.default_accept_hotkey)
    result = prompt.run()

    assert result.selections == TEST_CHOICES[1:4], f"Unexpected selections: {result.selections}"
    assert result.end_status == "accept"
    assert result.current == TEST_CHOICES[4]
    assert prompt.current_preview == "7: Hello World"
    assert prompt.obj == EXPECTED_RECORDING, f"Unexpected recording: {prompt.obj}"

    # currently doesn't work because automated hotkeys use endpoint with hardcoded 'start' trigger
    # assert result.trigger == Config.default_accept_hotkey


@logging_setup.attach
def test_quit():
    prompt = prompt_builder()
    prompt.mod.automate("ctrl-q")
    assert prompt.run().end_status == "quit"


@pytest.mark.parametrize(["action", "end_status"], [("accept", "accept"), ("abort", "abort")])
@logging_setup.attach
def test_ending_prompt_with_base_action(action, end_status):
    prompt = prompt_builder()
    prompt.mod.automate_actions(action)
    assert prompt.run().end_status == end_status


if __name__ == "__main__":
    prompt = prompt_builder()
    logging_setup.attach(prompt.run)()
