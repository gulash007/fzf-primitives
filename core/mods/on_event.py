from __future__ import annotations

import functools
from pathlib import Path
from typing import Callable, Literal, Self

import clipboard
from thingies import shell_command

from ..FzfPrompt.constants import SHELL_COMMAND
from ..FzfPrompt.options.actions import ShellCommandActionType
from ..FzfPrompt.options.events import Hotkey, Situation
from ..FzfPrompt import (
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


type FileBrowser = Literal["VS Code", "VS Code - Insiders"]
FILE_BROWSERS: dict[FileBrowser, str] = {"VS Code": "code", "VS Code - Insiders": "code-insiders"}


class OnEvent[T, S]:
    def __init__(self, *events: Hotkey | Situation, conflict_resolution: ConflictResolution = "raise error"):
        self._bindings: list[Binding] = []
        self._events: list[Hotkey | Situation] = list(events)
        self._conflict_resolution: ConflictResolution = conflict_resolution

    def run(self, name: str, *actions: Action) -> Self:
        self._bindings.append(Binding(name, *actions))
        return self

    def run_function(self, name: str, function: ServerCallFunction[T, S]) -> Self:
        return self.run(name, ServerCall(function, action_type="execute"))

    def run_shell_command(self, name: str, command: str, command_type: ShellCommandActionType = "execute") -> Self:
        return self.run(name, ShellCommand(command, action_type=command_type))

    def end_prompt(
        self, name: str, end_status: EndStatus, post_processor: Callable[[PromptData[T, S]], None] | None = None
    ):
        self.run(name, PromptEndingAction(end_status, post_processor))

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event in self._events:
            prompt_data.action_menu.add(
                event,
                functools.reduce(lambda b1, b2: b1 + b2, self._bindings),
                conflict_resolution=self._conflict_resolution,
            )

    # presets
    @property
    def accept(self):
        """Ends prompt with status 'accept'"""
        return self.end_prompt("accept", "accept")

    @property
    def abort(self):
        """Ends prompt with status 'abort'"""
        return self.end_prompt("abort", "abort")

    @property
    def quit(self):
        """Ends prompt with status 'quit'"""
        return self.end_prompt("quit", "quit")

    @property
    def clip(self):
        return self.run_shell_command("clip", SHELL_COMMAND.clip_selections)

    @property
    def select(self):
        return self.run("select", "select")

    @property
    def select_all(self):
        return self.run("select", "select-all")

    @property
    def toggle(self):
        return self.run("toggle", "toggle")

    @property
    def toggle_all(self):
        return self.run("toggle all", "toggle-all")

    @property
    def refresh_preview(self):
        return self.run("refresh preview", "refresh-preview")

    @property
    def toggle_preview(self):
        return self.run("toggle preview", "toggle-preview")

    @property
    def jump(self):
        return self.run("jump", "jump")

    @property
    def jump_accept(self):
        return self.run("jump and accept", "jump-accept")

    @property
    def clip_current_preview(self):
        return self.run_function("clip current preview", clip_current_preview)

    @property
    def clip_options(self):
        return self.run_function("clip options", clip_options)

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
