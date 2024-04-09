# Syntax sugar layer
from __future__ import annotations

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
    Preview,
    PromptData,
    PromptEndingAction,
    Result,
    ServerCall,
    ServerCallFunction,
    ShellCommand,
)
from .monitoring.Logger import get_logger

logger = get_logger()


def quit_app(prompt_data: PromptData):
    raise ExitLoop(f"Exiting app with\n{prompt_data.result}")


def clip_current_preview(prompt_data: PromptData):
    clipboard.copy(prompt_data.get_current_preview())


def clip_options(prompt_data: PromptData):
    clipboard.copy(prompt_data.options.pretty())


class binding_preset:
    def __init__(self, name: str, *actions: Action | ShellCommand) -> None:
        self._name = name
        self._actions = actions

    def __get__[T, S](self, obj: on_event[T, S], objtype=None) -> on_event[T, S]:
        return obj.run(self._name, *self._actions)


class on_event[T, S]:
    accept = binding_preset("accept", "accept")
    abort = binding_preset("abort", "abort")
    clip = binding_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    toggle_all = binding_preset("toggle all", "toggle-all")
    select_all = binding_preset("select all", "select-all")
    quit = binding_preset("quit", PromptEndingAction("abort", quit_app))
    clip_current_preview = binding_preset("clip current preview", ServerCall(clip_current_preview))
    clip_options = binding_preset("clip options", ServerCall(clip_options))

    def view_logs_in_terminal(self, log_file_path: str | Path):
        command = f"less +F '{log_file_path}'"
        return self.run("copy command to view logs in terminal", ServerCall(lambda pd: clipboard.copy(command)))

    def __init__(self, prompt_data: PromptData[T, S], event: Hotkey | FzfEvent):
        self.prompt_data = prompt_data
        self.event: Hotkey | FzfEvent = event

    def run(self, name: str, *actions: Action | ShellCommand) -> Self:
        self.prompt_data.action_menu.add(self.event, Binding(name, *actions))
        return self

    def run_server_call(self, name: str, function: ServerCallFunction[T, S]) -> Self:
        return self.run(name, ServerCall(function))


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
        return obj.custom(
            self._name, self._command, self._window_size, self._window_position, self._preview_label, self._store_output
        )


class preview[T, S]:
    basic = preview_preset("basic", preview_basic)
    basic_indexed = preview_preset("basic indexed", preview_basic_indexed)

    def __init__(self, prompt_data: PromptData[T, S], hotkey: Hotkey | None = None, main: bool = False):
        self.prompt_data = prompt_data
        self.hotkey: Hotkey | None = hotkey
        self.main = main

    def file(self, language: str = "python", theme: str = "Solarized (light)"):
        """Parametrized preset for viewing files"""

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

        self.custom("View File", view_file)

    def custom(
        self,
        name: str,
        command: str | ServerCallFunction[T, S],
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        self.prompt_data.add_preview(
            Preview(name, command, self.hotkey, window_size, window_position, preview_label, store_output),
            main=self.main,
        )


class post_processing[T, S]:
    def __init__(self, prompt_data: PromptData[T, S]) -> None:
        self.prompt_data = prompt_data

    # TODO: clip presented selections or the selections passed as choices?
    def clip_output(self, transformer: Callable[[Result[T]], str] = str):
        raise NotImplementedError("clip output not implemented yet")

    # TODO: Check correctness or if it's needed
    def exit_round_on(self, predicate: Callable[[PromptData[T, S]], bool], message: str = ""):
        def exit_round_on_predicate(prompt_data: PromptData[T, S]):
            if predicate(prompt_data):
                raise ExitRound(message)

        self.custom(exit_round_on_predicate)

    def exit_round_when_aborted(self, message: str = "Aborted!"):
        return self.exit_round_on(lambda prompt_data: prompt_data.result.end_status == "abort", message)

    def exit_round_on_empty_selections(self, message: str = "Selection empty!"):
        return self.exit_round_on(lambda prompt_data: not prompt_data.result, message)

    def custom(self, function: Callable[[PromptData[T, S]], None]):
        self.prompt_data.add_post_processor(function)
        return self


class Mod[T, S]:
    def __init__(self, prompt_data: PromptData[T, S]):
        self._prompt_data = prompt_data
        self._options = Options()

    # TODO: on_event hotkey to cycle through previews
    def on_event(self, event: Hotkey | FzfEvent, check_for_conflicts: bool = True):
        if check_for_conflicts:
            if binding := self._prompt_data.action_menu.bindings.get(event):
                raise RuntimeError(f"Event {event} already has a binding: {binding}")
        return on_event(self._prompt_data, event)

    def preview(self, hotkey: Hotkey | None = None, check_for_conflicts: bool = True, *, main: bool = False):
        if hotkey and check_for_conflicts:
            if binding := self._prompt_data.action_menu.bindings.get(hotkey):
                raise RuntimeError(f"Event {hotkey} already has a binding: {binding}")
        return preview(self._prompt_data, hotkey, main=main)

    @property
    def lastly(self):
        """Applied from left to right"""
        return post_processing(self._prompt_data)

    @property
    def options(self) -> Options:
        return self._options

    def apply_options(self):
        self._prompt_data.options += self.options

    def automate(self, *to_execute: Binding | Hotkey):
        self._prompt_data.action_menu.automate(*to_execute)

    def automate_actions(self, *actions: Action):
        self._prompt_data.action_menu.automate_actions(*actions)

    @property
    def default(self) -> Self:
        self.on_event("ctrl-c").clip
        self.on_event("ctrl-y").clip_options
        self.lastly.exit_round_when_aborted()
        return self
