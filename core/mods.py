# Syntax sugar layer
from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal, Self

import clipboard
from thingies import shell_command

from .FzfPrompt.constants import SHELL_COMMAND
from .FzfPrompt.exceptions import ExitLoop, ExitRound
from .FzfPrompt.options import FzfEvent, Hotkey, Options, Position
from .FzfPrompt.Prompt import (
    Action,
    Binding,
    EndStatus,
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


def quit_app(prompt_data: PromptData):
    raise ExitLoop(f"Exiting app with\n{prompt_data.result}")


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
    accept = binding_preset("accept", PromptEndingAction("accept"))
    abort = binding_preset("abort", PromptEndingAction("abort"))
    quit = binding_preset("quit", PromptEndingAction("abort", quit_app))
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

    def __init__(self, prompt_data: PromptData[T, S], event: Hotkey | FzfEvent):
        self.prompt_data = prompt_data
        self.event: Hotkey | FzfEvent = event

    def run(self, name: str, *actions: Action | ShellCommand) -> Self:
        self.prompt_data.action_menu.add(self.event, Binding(name, *actions))
        return self

    def run_function(self, name: str, function: ServerCallFunction[T, S]) -> Self:
        return self.run(name, ServerCall(function))

    def run_shell_command(self, name: str, command: str, command_type: ShellCommandActionType = "execute") -> Self:
        return self.run(name, (ShellCommand(command), command_type))

    def end_prompt(
        self, name: str, end_status: EndStatus, post_processor: Callable[[PromptData[T, S]], None] | None = None
    ):
        return self.run(name, PromptEndingAction(end_status, post_processor))


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


class preview[T, S]:
    basic = preview_preset("basic", preview_basic)
    basic_indexed = preview_preset("basic indexed", preview_basic_indexed)

    def __init__(self, prompt_data: PromptData[T, S], hotkey: Hotkey | None = None, main: bool = False):
        self.prompt_data = prompt_data
        self.hotkey: Hotkey | None = hotkey
        self.main = main

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

    # TODO: Add option to change back to main preview automatically after changing selection
    def custom(
        self,
        name: str,
        command: str | PreviewFunction[T, S],
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        self.prompt_data.add_preview(
            Preview(name, command, self.hotkey, window_size, window_position, preview_label, store_output),
            main=self.main,
        )

    def simple(self, command: str):
        """As if just passing --preview 'command' option to fzf with no additional support"""
        self.prompt_data.options.preview(command)


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

        return self.custom(exit_round_on_predicate)

    def exit_round_when_aborted(self, message: str = "Aborted!"):
        return self.exit_round_on(lambda prompt_data: prompt_data.result.end_status == "abort", message)

    def exit_round_on_empty_selections(self, message: str = "Selection empty!"):
        return self.exit_round_on(lambda prompt_data: not prompt_data.result, message)

    def custom(self, function: Callable[[PromptData[T, S]], None]):
        self.prompt_data.add_post_processor(function)
        return self


class BindingConflict(Exception):
    pass


class Mod[T, S]:
    def __init__(self, prompt_data: PromptData[T, S]):
        self._prompt_data = prompt_data
        self._options = Options()

    # TODO: on_event hotkey to cycle through previews
    def on_event(self, event: Hotkey | FzfEvent, check_for_conflicts: bool = True):
        if check_for_conflicts:
            if binding := self._prompt_data.action_menu.bindings.get(event):
                raise BindingConflict(f"Event {event} already has a binding: {binding}")
        return on_event(self._prompt_data, event)

    def preview(self, hotkey: Hotkey | None = None, check_for_conflicts: bool = True, *, main: bool = False):
        if hotkey and check_for_conflicts:
            if binding := self._prompt_data.action_menu.bindings.get(hotkey):
                raise BindingConflict(f"Event {hotkey} already has a binding: {binding}")
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
        self.on_event("ctrl-x").clip_current_preview
        self.on_event("ctrl-y").clip_options
        return self
