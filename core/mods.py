# Syntax sugar layer
from __future__ import annotations

import functools
from typing import Any, Generic, Literal, ParamSpec, Protocol

import clipboard

from .FzfPrompt.commands import SHELL_COMMAND
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.options import FzfEvent, Hotkey, Options, Position
from .FzfPrompt.Prompt import (
    Action,
    Binding,
    PostProcessAction,
    Preview,
    PromptData,
    PromptEndingAction,
    Result,
    ServerCall,
    ShellCommand,
)
from .monitoring.Logger import get_logger

P = ParamSpec("P")
logger = get_logger()


class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...


def add_options(added_options: Options):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def adding_options(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = prompt_data.options + added_options
            return func(prompt_data, *args, **kwargs)

        return adding_options

    return decorator


multiselect = add_options(Options().multiselect)
ansi = add_options(Options().ansi)
no_sort = add_options(Options().no_sort)


def exit_round_when_aborted(message: str = ""):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def exiting_round_when_aborted(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            result = func(prompt_data, *args, **kwargs)
            if result.end_status == "abort":
                logger.info(message)
                raise ExitRound(message)
            return result

        return exiting_round_when_aborted

    return decorator


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: preview label


def quit_app(prompt_data: PromptData):
    sep = "\n\t"
    raise ExitLoop(
        f"Exiting app with\nquery: {prompt_data.result.query}\nselections:{sep}{sep.join(prompt_data.result)}"
    )


def clip_current_preview(prompt_data: PromptData):
    clipboard.copy(prompt_data.get_current_preview())


class event_preset:
    def __init__(self, name: str, *actions: Action, end_prompt: PromptEndingAction | Literal[False] = False) -> None:
        self._name = name
        self._actions = actions
        self._end_prompt: PromptEndingAction | Literal[False] = end_prompt

    def __get__(self, obj: on_event, objtype=None):
        return obj(self._name, *self._actions, end_prompt=self._end_prompt)


def pipe_results(prompt_data: PromptData, query: str, selections: list[str]):
    prompt_data.result.query = "test"
    prompt_data.result.event = "enter"
    prompt_data.result.end_status = "accept"
    prompt_data.result.extend(selections)
    logger.debug("Piping results")
    logger.debug(prompt_data.result)


# TODO: chaining?
class on_event:
    clip = event_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    toggle_all = event_preset("toggle all", "toggle-all")
    select_all = event_preset("select all", "select-all")
    quit = event_preset("quit", PostProcessAction(quit_app), end_prompt="abort")
    clip_current_preview = event_preset("clip current preview", ServerCall(clip_current_preview))

    def __init__(self, event: Hotkey | FzfEvent):
        self.event: Hotkey | FzfEvent = event

    def __call__(self, name: str, *actions: Action, end_prompt: PromptEndingAction | Literal[False] = False) -> Any:
        def decorator(func: Moddable[P]) -> Moddable[P]:
            def wrapper(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
                prompt_data.action_menu.add(self.event, Binding(name, *actions, end_prompt=end_prompt))
                return func(prompt_data, *args, **kwargs)

            return wrapper

        return decorator


PRESET_PREVIEWS = {
    "basic": "/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/.env/bin/python3.11 -m fzf_primitives.experimental.core.actions.preview_basic {q} {} {+}"
}


def add_preview(
    name: str,
    command: str,
    hotkey: Hotkey,
    window_size: int | str = "50%",
    window_position: Position = "right",
):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.add_preview(Preview(name, command, hotkey, window_size, window_position))
            return func(prompt_data, *args, **kwargs)

        return with_preview

    return decorator


class preview:
    basic = functools.partial(add_preview, "basic", PRESET_PREVIEWS["basic"])
    custom = staticmethod(add_preview)  # without staticmethod get_preview is treated like instance method

    @staticmethod
    def file(language: str = "python", theme: str = "Solarized (light)"):
        language_arg = f"--language {language}" if language else ""
        theme_arg = f'--theme "{theme}"' if theme else ""
        return functools.partial(
            add_preview,
            "View File",
            f"python3.11 -m fzf_primitives.core.actions.view_file {{q}} {{+}} {language_arg} {theme_arg}",
        )


def clip_output(func: Moddable[P]) -> Moddable[P]:
    def clipping_output(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
        result = func(prompt_data, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
