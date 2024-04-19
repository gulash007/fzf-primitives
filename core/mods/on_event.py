from __future__ import annotations

import functools
from pathlib import Path
from typing import Callable, Literal, Self

import clipboard
from thingies import shell_command

from ..FzfPrompt.constants import SHELL_COMMAND
from ..FzfPrompt.options.actions import ShellCommandActionType
from ..FzfPrompt.options.events import Hotkey, PromptEvent
from ..FzfPrompt.Prompt import (
    Action,
    Binding,
    ConflictResolution,
    EndStatus,
    PromptData,
    PromptEndingAction,
    ServerCall,
    ServerCallFunction,
    ShellCommand,
)


def clip_current_preview(prompt_data: PromptData):
    clipboard.copy(prompt_data.get_current_preview())


def clip_options(prompt_data: PromptData):
    clipboard.copy(str(prompt_data.options))


class binding_preset:
    def __init__(self, name: str, *actions: Action | ShellCommand) -> None:
        self._name = name
        self._actions = actions

    def __get__[T, S](self, obj: OnEvent[T, S], objtype=None) -> OnEvent[T, S]:
        return obj.run(self._name, *self._actions)


type FileBrowser = Literal["VS Code", "VS Code - Insiders"]
FILE_BROWSERS: dict[FileBrowser, str] = {"VS Code": "code", "VS Code - Insiders": "code-insiders"}


class OnEvent[T, S]:
    def __init__(self, *, conflict_resolution: ConflictResolution = "raise error"):
        self._bindings: list[Binding] = []
        self._events: list[Hotkey | PromptEvent] = []
        self._conflict_resolution: ConflictResolution = conflict_resolution

    def set_event(self, event: Hotkey | PromptEvent):
        self._events.append(event)

    def run(self, name: str, *actions: Action | ShellCommand) -> Self:
        self._bindings.append(Binding(name, *actions))
        return self

    def run_function(self, name: str, function: ServerCallFunction[T, S]) -> Self:  # noqa: F821
        return self.run(name, (ServerCall(function), "execute"))

    def run_shell_command(self, name: str, command: str, command_type: ShellCommandActionType = "execute") -> Self:
        return self.run(name, (ShellCommand(command), command_type))

    def end_prompt(
        self, name: str, end_status: EndStatus, post_processor: Callable[[PromptData[T, S]], None] | None = None
    ):
        return self.run(name, PromptEndingAction(end_status, post_processor))

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event in self._events:
            prompt_data.action_menu.add(
                event,
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
