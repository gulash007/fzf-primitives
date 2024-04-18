# Syntax sugar layer
from __future__ import annotations

import functools
from pathlib import Path
from typing import Callable, Literal, Self

import clipboard
from thingies import shell_command

from .FzfPrompt.constants import SHELL_COMMAND
from .FzfPrompt.exceptions import ExitRound
from .FzfPrompt.options import PromptEvent, Hotkey, Options, Position
from .FzfPrompt.Prompt import (
    Action,
    Binding,
    ConflictResolution,
    EndStatus,
    PostProcessor,
    Preview,
    PreviewFunction,
    PromptData,
    PromptEndingAction,
    Result,
    ServerCall,
    ServerCallFunction,
    ShellCommand,
    ShellCommandActionType,
)
from .monitoring.Logger import get_logger

logger = get_logger()


def clip_current_preview(prompt_data: PromptData):
    clipboard.copy(prompt_data.get_current_preview())


def clip_options(prompt_data: PromptData):
    clipboard.copy(str(prompt_data.options))


class binding_preset:
    def __init__(self, name: str, *actions: Action | ShellCommand) -> None:
        self._name = name
        self._actions = actions

    def __get__[T, S](self, obj: on_event[T, S], objtype=None) -> on_event[T, S]:
        return obj.run(self._name, *self._actions)


type FileBrowser = Literal["VS Code", "VS Code - Insiders"]
FILE_BROWSERS: dict[FileBrowser, str] = {"VS Code": "code", "VS Code - Insiders": "code-insiders"}


class on_event[T, S]:
    def __init__(self, event: Hotkey | FzfEvent, *, conflict_resolution: ConflictResolution = "raise error"):
        self._bindings: list[Binding] = []
        self._event: Hotkey | FzfEvent = event
        self._conflict_resolution: ConflictResolution = conflict_resolution

    def run(self, name: str, *actions: Action | ShellCommand) -> Self:
        self._bindings.append(Binding(name, *actions))
        return self

    def run_function(self, name: str, function: ServerCallFunction[T, S]) -> Self:
        return self.run(name, ServerCall(function))

    def run_shell_command(self, name: str, command: str, command_type: ShellCommandActionType = "execute") -> Self:
        return self.run(name, (ShellCommand(command), command_type))

    def end_prompt(
        self, name: str, end_status: EndStatus, post_processor: Callable[[PromptData[T, S]], None] | None = None
    ):
        return self.run(name, PromptEndingAction(end_status, post_processor))

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        prompt_data.action_menu.add(
            self._event,
            functools.reduce(lambda b1, b2: b1 + b2, self._bindings),
            conflict_resolution=self._conflict_resolution,
        )

    # presets
    accept = binding_preset("accept", PromptEndingAction("accept"))
    abort = binding_preset("abort", PromptEndingAction("abort"))
    quit = binding_preset("quit", PromptEndingAction("quit"))
    clip = binding_preset("clip selections", ShellCommand(SHELL_COMMAND.clip_selections))
    select = binding_preset("select", "select")
    select_all = binding_preset("select all", "select-all")
    toggle = binding_preset("toggle", "toggle")
    toggle_all = binding_preset("toggle all", "toggle-all")
    refresh_preview = binding_preset("refresh preview", "refresh-preview")
    toggle_preview = binding_preset("toggle preview", "toggle-preview")
    jump = binding_preset("jump", "jump")
    jump_accept = binding_preset("jump and accept", "jump-accept")
    jump_select = binding_preset("jump and select", "jump", "select")
    clip_current_preview = binding_preset("clip current preview", ServerCall(clip_current_preview))
    clip_options = binding_preset("clip options", ServerCall(clip_options))

    def view_logs_in_terminal(self, log_file_path: str | Path):
        command = f"less +F '{log_file_path}'"
        return self.run("copy command to view logs in terminal", ServerCall(lambda pd: clipboard.copy(command)))

    def open_files(self, relative_to: str | Path = ".", app: FileBrowser = "VS Code"):
        command = FILE_BROWSERS[app]
        return self.run_function(
            f"open files in {app}",
            lambda pd: shell_command(
                [command, *[f"{relative_to}/{selection}" for selection in pd.current_state.lines]], shell=False
            ),
        )


def preview_basic(prompt_data: PromptData):
    sep = "\n\t"
    query, line, lines = (cs := prompt_data.current_state).query, cs.single_line, cs.lines
    return f"query: {query}\nselection: {line}\nselections:\n\t{sep.join(lines)}"


def preview_basic_indexed(prompt_data: PromptData):
    sep = "\n\t"
    cs = prompt_data.current_state
    query, index, line, indices, lines = cs.query, cs.single_index, cs.single_line, cs.indices, cs.lines
    indexed_selections = [f"{i}\t{selection}" for i, selection in zip(indices, lines)]
    return f"query: {query}\nselection: {index} {line}\nselections:\n\t{sep.join(indexed_selections)}"


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
        return obj.custom(
            self._name, self._command, self._window_size, self._window_position, self._preview_label, self._store_output
        )


# TODO: Add option to change back to main preview automatically after changing selection
class preview[T, S]:

    def __init__(
        self,
        hotkey: Hotkey | None = None,
        *,
        conflict_resolution: ConflictResolution = "raise error",
        main: bool = False,
    ):
        self._preview_adder: Callable[[PromptData[T, S]]]
        self._hotkey: Hotkey | None = hotkey
        self._conflict_resolution: ConflictResolution = conflict_resolution
        self._main = main

    def custom(
        self,
        name: str,
        command: str | PreviewFunction[T, S],
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ) -> None:
        self._preview_adder = lambda prompt_data: prompt_data.add_preview(
            Preview[T, S](name, command, self._hotkey, window_size, window_position, preview_label, store_output),
            conflict_resolution=self._conflict_resolution,
            main=self._main,
        )

    def simple(self, command: str):
        """As if just passing --preview 'command' option (and --bind '<hotkey>:change-preview(...))') to fzf with no additional support"""

        def add_simple_preview(prompt_data: PromptData[T, S]):
            prompt_data.options.preview(command)
            if self._hotkey:
                prompt_data.options.bind_shell_command(self._hotkey, command, "change-preview")

        self._preview_adder = add_simple_preview

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        self._preview_adder(prompt_data)

    # presets
    basic = preview_preset("basic", preview_basic)
    basic_indexed = preview_preset("basic indexed", preview_basic_indexed)

    def file(self, language: str = "python", theme: str = "Solarized (light)"):
        """Parametrized preset for viewing files"""

        def view_file(prompt_data: PromptData[T, S]):
            command = ["bat", "--color=always"]
            if language:
                command.extend(("--language", language))
            if theme:
                command.extend(("--theme", theme))
            command.append("--")  # Fixes file names starting with a hyphen
            command.extend(prompt_data.current_state.lines)
            return shell_command(command)

        self.custom("View File", view_file)


class post_processing[T, S]:
    def __init__(self) -> None:
        self._post_processors: list[PostProcessor[T, S]] = []

    def custom(self, function: Callable[[PromptData[T, S]], None]):
        self._post_processors.append(function)
        return self

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for post_processor in self._post_processors:
            prompt_data.add_post_processor(post_processor)

    # presets
    # TODO: clip presented selections or the selections passed as choices?
    def clip_output(self, transformer: Callable[[Result[T]], str] = str):
        raise NotImplementedError("clip output not implemented yet")

    # TODO: Check correctness or if it's needed
    def exit_round_on(self, predicate: Callable[[PromptData[T, S]], bool], message: str = ""):
        def exit_round_on_predicate(prompt_data: PromptData[T, S]):
            if predicate(prompt_data):
                raise ExitRound(message)

        return self.custom(exit_round_on_predicate)

    def exit_round_when_aborted(self, message: str = "Aborted!"):
        return self.exit_round_on(lambda prompt_data: prompt_data.result.end_status == "abort", message)

    def exit_round_on_empty_selections(self, message: str = "Selection empty!"):
        return self.exit_round_on(lambda prompt_data: not prompt_data.result, message)


class Mod[T, S]:
    def __init__(self, prompt_data: PromptData[T, S]):
        self._prompt_data = prompt_data
        self._mods: list[Callable[[PromptData], None]] = []
        self._options = Options()

    def apply(self):
        try:
            for mod in self._mods:
                mod(self._prompt_data)
            self._prompt_data.options += self.options
        finally:
            self.clear()

    def clear(self):
        self._mods = []
        self._options = Options()

    # TODO: on_event hotkey to cycle through previews
    def on_event(self, event: Hotkey | FzfEvent, *, conflict_resolution: ConflictResolution = "raise error"):
        on_event_mod = on_event[T, S](event, conflict_resolution=conflict_resolution)
        self._mods.append(on_event_mod)
        return on_event_mod

    def preview(
        self,
        hotkey: Hotkey | None = None,
        *,
        conflict_resolution: ConflictResolution = "raise error",
        main: bool = False,
    ):
        preview_mod = preview[T, S](hotkey, conflict_resolution=conflict_resolution, main=main)
        self._mods.append(preview_mod)
        return preview_mod

    @property
    def lastly(self):
        """Applied from left to right"""
        post_processing_mod = post_processing[T, S]()
        self._mods.append(post_processing_mod)
        return post_processing_mod

    @property
    def options(self) -> Options:
        return self._options

    def automate(self, *to_execute: Binding | Hotkey):
        self._mods.append(lambda pd: pd.action_menu.automate(*to_execute))

    def automate_actions(self, *actions: Action):
        self._mods.append(lambda pd: pd.action_menu.automate_actions(*actions))

    @property
    def default(self) -> Self:
        self.on_event("ctrl-c").clip
        self.on_event("ctrl-x").clip_current_preview
        self.on_event("ctrl-y").clip_options
        return self
