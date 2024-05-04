from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Literal, Self

import pyperclip

from ..FzfPrompt import (
    Action,
    Binding,
    ChoicesGetter,
    ConflictResolution,
    EndStatus,
    PromptData,
    PromptEndingAction,
    ReloadChoices,
    ServerCall,
    ServerCallFunction,
    ShellCommand,
)
from ..FzfPrompt.constants import SHELL_COMMAND
from ..FzfPrompt.options.actions import BaseAction, ShellCommandActionType
from ..FzfPrompt.options.events import Hotkey, Situation


def clip_current_preview(prompt_data: PromptData):
    pyperclip.copy(prompt_data.get_current_preview())


def clip_options(prompt_data: PromptData):
    pyperclip.copy(str(prompt_data.options))


type FileEditor = Literal["VS Code", "VS Code - Insiders", "Vi", "Vim", "NeoVim", "Nano"]
FILE_EDITORS: dict[FileEditor, str] = {
    "VS Code": "code",
    "VS Code - Insiders": "code-insiders",
    "Vi": "vi",
    "Vim": "vim",
    "NeoVim": "nvim",
    "Nano": "nano",
}


class OnEvent[T, S]:
    def __init__(self, *events: Hotkey | Situation, conflict_resolution: ConflictResolution = "raise error"):
        self._bindings: dict[Hotkey | Situation, Binding] = {}
        self._events: list[Hotkey | Situation] = list(events)
        self._conflict_resolution: ConflictResolution = conflict_resolution

    def run(self, name: str, *actions: Action) -> Self:
        for event in self._events:
            self._add_binding(event, name, *actions)
        return self

    def _add_binding(self, event: Hotkey | Situation, name: str, *actions: Action):
        if event not in self._bindings:
            self._bindings[event] = Binding(name, *actions)
        else:
            self._bindings[event] += Binding(name, *actions)

    def run_function(
        self, name: str, function: ServerCallFunction[T, S], *base_actions: BaseAction, silent: bool = False
    ) -> Self:
        return self.run(
            name, ServerCall(function, command_type="execute-silent" if silent else "execute"), *base_actions
        )

    def run_shell_command(
        self, name: str, command: str, *base_actions: BaseAction, command_type: ShellCommandActionType = "execute"
    ) -> Self:
        return self.run(name, ShellCommand(command, command_type=command_type), *base_actions)

    def reload_choices(self, choices_getter: ChoicesGetter[T, S], *, sync: bool = False):
        return self.run(f"reload choices{' (sync)' if sync else ''}", ReloadChoices(choices_getter, sync=sync))

    def end_prompt(
        self, name: str, end_status: EndStatus, post_processor: Callable[[PromptData[T, S]], None] | None = None
    ):
        """Post-processor is called after the prompt has ended and before common post-processors are applied (defined in Mod.lastly)"""
        for event in self._events:
            self._add_binding(event, name, PromptEndingAction(end_status, event, post_processor))

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event, binding in self._bindings.items():
            prompt_data.add_binding(event, binding, conflict_resolution=self._conflict_resolution)

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
        return self.run("select all", "select-all")

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
        return self.run_function("copy command to view logs in terminal", lambda pd: pyperclip.copy(command))

    def open_files(
        self, file_getter: Callable[[PromptData[T, S]], list[str]] | None = None, app: FileEditor = "VS Code"
    ):
        """❗ VS Code doesn't handle files with leading or trailing spaces/tabs/newlines (it strips them)
        NeoVim opens them all"""
        file_getter = file_getter or (lambda pd: pd.current_state.lines)
        command = FILE_EDITORS[app]
        return self.run_function(f"open files in {app}", lambda pd: subprocess.run([command, "--", *file_getter(pd)]))
