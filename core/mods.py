# Syntax sugar layer
from __future__ import annotations

import functools
from pathlib import Path
from typing import Callable, Self

import clipboard
from thingies import shell_command

from .FzfPrompt.constants import SHELL_COMMAND
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.options import FzfEvent, Hotkey, Options, Position
from .FzfPrompt.Prompt import (
    Action,
    Binding,
    Result,
    Preview,
    PreviewFunction,
    PromptData,
    PromptEndingAction,
    ServerCall,
    ShellCommand,
)
from .monitoring.Logger import get_logger

logger = get_logger()


type Moddable[T, S] = Callable[[PromptData[T, S]], Result[T]]


defaults = Options().defaults
multiselect = Options().multiselect
ansi = Options().ansi
no_sort = Options().no_sort
cycle = Options().cycle
no_mouse = Options().no_mouse
header_first = Options().header_first
disable_search = Options().disable_search


# TODO: Check correctness or if it's needed
def exit_round_on(predicate: Callable[[PromptData], bool], message: str = ""):
    def decorator[T, S](func: Moddable[T, S]) -> Moddable[T, S]:
        def exiting_round_on(prompt_data: PromptData[T, S]):
            result = func(prompt_data)
            if predicate(prompt_data):
                logger.info(message)
                raise ExitRound(message)
            return result

        return exiting_round_on

    return decorator


def exit_round_when_aborted(message: str = "Aborted!"):
    return exit_round_on(lambda prompt_data: prompt_data.result.end_status == "abort", message)


def exit_round_on_empty_selections(message: str = "Selection empty!"):
    return exit_round_on(lambda prompt_data: not prompt_data.result, message)


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


class on_event[T, S]:
    accept = binding_preset("accept", "accept")
    abort = binding_preset("abort", "abort")
    clip = binding_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    toggle_all = binding_preset("toggle all", "toggle-all")
    select_all = binding_preset("select all", "select-all")
    quit = binding_preset("quit", PromptEndingAction("abort", quit_app))
    clip_current_preview = binding_preset("clip current preview", ServerCall(clip_current_preview))

    def view_logs_in_terminal(self, log_file_path: str | Path):
        command = f"less +F '{log_file_path}'"
        return self.run("copy command to view logs in terminal", ServerCall(lambda pd: clipboard.copy(command)))

    def __init__(self, event: Hotkey | FzfEvent, name: str | None = None):
        self.event: Hotkey | FzfEvent = event
        self.name = name  # TODO: Use it?
        self.binding_constructors: list[Callable[[], Binding]] = []

    def run(self, name: str, *actions: Action | ShellCommand) -> Self:
        self.binding_constructors.append(lambda: Binding(name, *actions))
        return self

    def __call__(self, func: Moddable[T, S]) -> Moddable[T, S]:
        @functools.wraps(func)
        def with_added_binding(prompt_data: PromptData[T, S]):
            bindings = (bc() for bc in self.binding_constructors)
            prompt_data.action_menu.add(self.event, functools.reduce(lambda b1, b2: b1 + b2, bindings))
            return func(prompt_data)

        return with_added_binding


def automate[T, S](*to_execute: Binding | Hotkey):
    def decorator(func: Moddable[T, S]) -> Moddable[T, S]:
        def with_automatization(prompt_data: PromptData):
            prompt_data.action_menu.automate(*to_execute)
            return func(prompt_data)

        return with_automatization

    return decorator


def automate_actions[T, S](*actions: Action):
    def decorator(func: Moddable[T, S]) -> Moddable[T, S]:
        def with_automatization(prompt_data: PromptData[T, S]):
            prompt_data.action_menu.automate_actions(*actions)
            return func(prompt_data)

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


class preview[T, S]:
    basic = preview_preset("basic", preview_basic)
    basic_indexed = preview_preset("basic indexed", preview_basic_indexed)

    def __init__(self, hotkey: Hotkey, *, main: bool = False):
        self.hotkey: Hotkey = hotkey
        self.main = main

    def file(self, language: str = "python", theme: str = "Solarized (light)"):
        def view_file(
            prompt_data: PromptData[T, S],
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
        command: str | PreviewFunction[T, S],
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        def decorator(func: Moddable[T, S]) -> Moddable[T, S]:
            def with_preview(prompt_data: PromptData[T, S]):
                prompt_data.add_preview(
                    Preview(name, command, self.hotkey, window_size, window_position, preview_label, store_output),
                    main=self.main,
                )
                return func(prompt_data)

            return with_preview

        return decorator


def clip_output[T, S](output_processor: Callable[[T], str] | None = None):
    def decorator(func: Moddable[T, S]) -> Moddable[T, S]:
        def clipping_output(prompt_data: PromptData[T, S]):
            result = func(prompt_data)
            to_clip = map(output_processor or str, result)
            clipboard.copy("\n".join(to_clip))
            return result

        return clipping_output

    return decorator
