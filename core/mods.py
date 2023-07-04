# Syntax sugar layer
from __future__ import annotations

import functools
from typing import Callable, Generic, ParamSpec, Protocol, Self

import clipboard
from thingies import shell_command

from .FzfPrompt.constants import SHELL_COMMAND
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.options import FzfEvent, Hotkey, Options, Position
from .FzfPrompt.Prompt import (
    Action,
    Binding,
    Preview,
    PromptData,
    PromptEndingAction,
    Result,
    ServerCall,
    PreviewFunction,
    ShellCommand,
)
from .monitoring.Logger import get_logger

P = ParamSpec("P")
logger = get_logger()


class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...


defaults = Options().defaults
multiselect = Options().multiselect
ansi = Options().ansi
no_sort = Options().no_sort
cycle = Options().cycle
no_mouse = Options().no_mouse
multiselect = Options().multiselect
header_first = Options().header_first
disable_search = Options().disable_search


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


class binding_preset:
    def __init__(self, name: str, *actions: Action | ShellCommand) -> None:
        self._name = name
        self._actions = actions

    def __get__(self, obj: on_event, objtype=None) -> on_event:
        return obj.run(self._name, *self._actions)


class on_event:
    accept = binding_preset("accept", "accept")
    abort = binding_preset("abort", "abort")
    clip = binding_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    toggle_all = binding_preset("toggle all", "toggle-all")
    select_all = binding_preset("select all", "select-all")
    quit = binding_preset("quit", PromptEndingAction("abort", quit_app))
    clip_current_preview = binding_preset("clip current preview", ServerCall(clip_current_preview))

    def __init__(self, event: Hotkey | FzfEvent):
        self.event: Hotkey | FzfEvent = event
        self.binding_constructors: list[Callable[[], Binding]] = []

    def run(self, name: str, *actions: Action | ShellCommand) -> Self:
        self.binding_constructors.append(lambda: Binding(name, *actions))
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
        command: str | PreviewFunction,
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
        command: str | PreviewFunction,
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
