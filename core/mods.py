# Syntax sugar layer
from __future__ import annotations
import functools
from pathlib import Path
from typing import Any, Callable, Generic, Literal, ParamSpec, Protocol, overload

import clipboard

from .exceptions import ExitLoop, ExitRound
from .FzfPrompt.ActionMenu import Action, PostProcessAction, ShellCommand
from .FzfPrompt.commands import ACTION, SHELL_COMMAND
from .FzfPrompt.decorators import constructor
from .FzfPrompt.options import Event, Hotkey, Options, Position
from .FzfPrompt.Previewer import Preview
from .FzfPrompt.Prompt import Result
from .FzfPrompt.PromptData import PromptData
from .FzfPrompt.Server import ServerCall
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


def exit_round_on_no_selection(message: str = ""):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def exiting_round_on_no_selection(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            if not (result := func(prompt_data, *args, **kwargs)) and not result.hotkey:
                logger.info(message)
                raise ExitRound(message)
            return result

        return exiting_round_on_no_selection

    return decorator


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: preview label


def quit_app(result: Result):
    sep = "\n\t"
    raise ExitLoop(f"Exiting app with\nquery: {result.query}\nselections:{sep}{sep.join(result)}")


def clip_current_preview(prompt_data: PromptData):
    clipboard.copy(prompt_data.get_current_preview())


class event_preset:
    def __init__(self, name: str, *actions: Action) -> None:
        self._name = name
        self._actions = actions

    def __get__(self, obj: on_event, objtype=None):
        return obj(self._name, *self._actions)


# TODO: chaining?
class on_event:
    clip = event_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    toggle_all = event_preset("toggle all", "toggle-all")
    select_all = event_preset("select all", "select-all")
    quit = event_preset("quit", PostProcessAction(quit_app))
    clip_current_preview = event_preset("clip current preview", ServerCall(clip_current_preview))

    def __init__(self, event: Hotkey | Event):
        self.event: Hotkey | Event = event

    def __call__(self, name: str, *actions: Action) -> Any:
        def decorator(func: Moddable[P]) -> Moddable[P]:
            def wrapper(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
                prompt_data.action_menu.add(name, self.event, *actions)
                return func(prompt_data, *args, **kwargs)

            return wrapper

        return decorator

    def post_process_action(self, post_processor: Callable[[Result], Any], custom_name: str | None = None):
        return self(custom_name or post_processor.__name__, PostProcessAction(post_processor))


PRESET_PREVIEWS = {
    "basic": "/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/.env/bin/python3.11 -m fzf_primitives.experimental.core.actions.preview_basic {q} {} {+}"
}


def add_preview(
    name: str,
    command: str | ServerCall,
    hotkey: Hotkey,
    window_size: int | str = "50%",
    window_position: Position = "right",
):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            cmd = ShellCommand(command) if isinstance(command, str) else command
            prompt_data.add_preview(Preview(name, cmd, hotkey, window_size, window_position))
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
