# Syntax sugar layer
from __future__ import annotations

import functools
from typing import Callable, Generic, Literal, ParamSpec, Protocol, Self

import clipboard
from copy import deepcopy

from .FzfPrompt.constants import SHELL_COMMAND
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
    ServerCallFunction,
    ShellCommand,
)
from .monitoring.Logger import get_logger
from thingies import shell_command

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

    def __get__(self, obj: on_event, objtype=None) -> on_event:
        return obj.run(self._name, *self._actions, end_prompt=self._end_prompt)


class on_event:
    clip = event_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    toggle_all = event_preset("toggle all", "toggle-all")
    select_all = event_preset("select all", "select-all")
    quit = event_preset("quit", PostProcessAction(quit_app), end_prompt="abort")
    clip_current_preview = event_preset("clip current preview", ServerCall(clip_current_preview))

    def __init__(self, event: Hotkey | FzfEvent):
        self.event: Hotkey | FzfEvent = event
        self.binding_constructors: list[Callable[[], Binding]] = []

    def run(self, name: str, *actions: Action, end_prompt: PromptEndingAction | Literal[False] = False) -> Self:
        self.binding_constructors.append(lambda: Binding(name, *deepcopy(actions), end_prompt=end_prompt))
        return self

    def __call__(self, func: Moddable[P]) -> Moddable[P]:
        def with_added_binding(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            bindings = (bc() for bc in self.binding_constructors)
            prompt_data.action_menu.add(self.event, functools.reduce(lambda b1, b2: b1 + b2, bindings))
            return func(prompt_data, *args, **kwargs)

        return with_added_binding


def automate(*to_execute: Binding | Hotkey):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_automatization(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.action_menu.automate(*to_execute)
            return func(prompt_data, *args, **kwargs)

        return with_automatization

    return decorator


def automate_actions(*actions: Action):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_automatization(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.action_menu.automate_actions(*actions)
            return func(prompt_data, *args, **kwargs)

        return with_automatization

    return decorator


def preview_basic(prompt_data: PromptData, query: str, selection: str, selections: list[str]):
    sep = "\n\t"
    return f"query: {query}\nselection: {selection}\nselections:\n\t{sep.join(selections)}"


def preview_basic_indexed(
    prompt_data: PromptData, query: str, selection: str, selections: list[str], index: int, indices: list[int]
):
    sep = "\n\t"
    indexed_selections = [f"{i}\t{selection}" for i, selection in zip(indices, selections)]
    return f"query: {query}\nselection: {selection}\nselections:\n\t{sep.join(indexed_selections)}"


class preview_preset:
    def __init__(
        self,
        name: str,
        command: str | ServerCallFunction,
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ) -> None:
        self._name = name
        self._command = command
        self._window_size = window_size
        self._window_position: Position = window_position
        self._preview_label = preview_label
        self._store_output = store_output

    def __get__(self, obj: preview, objtype=None):
        return obj(
            self._name, self._command, self._window_size, self._window_position, self._preview_label, self._store_output
        )


class preview:
    basic = preview_preset("basic", preview_basic)
    basic_indexed = preview_preset("basic indexed", preview_basic_indexed)

    def __init__(self, hotkey: Hotkey, *, main: bool = False):
        self.hotkey: Hotkey = hotkey
        self.main = main

    def file(self, language: str = "python", theme: str = "Solarized (light)"):
        def view_file(
            prompt_data: PromptData,
            selections: list[str],
        ):
            command = ["bat", "--color=always"]
            if language:
                command.extend(("--language", language))
            if theme:
                command.extend(("--theme", theme))
            command.append("--")  # Fixes file names starting with a hyphen
            command.extend(selections)
            return shell_command(command)

        return self("View File", view_file)

    def __call__(
        self,
        name: str,
        command: str | ServerCallFunction,
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        def decorator(func: Moddable[P]) -> Moddable[P]:
            def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
                prompt_data.add_preview(
                    Preview(name, command, self.hotkey, window_size, window_position, preview_label, store_output),
                    main=self.main,
                )
                return func(prompt_data, *args, **kwargs)

            return with_preview

        return decorator


def clip_output(output_processor: Callable[[str], str] | None = None):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def clipping_output(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            result = func(prompt_data, *args, **kwargs)
            to_clip = map(output_processor, result) if output_processor else result
            clipboard.copy("\n".join(to_clip))
            return result

        return clipping_output

    return decorator
