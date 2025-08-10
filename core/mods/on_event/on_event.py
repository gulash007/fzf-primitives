from __future__ import annotations

import subprocess
from abc import ABC
from pathlib import Path
from typing import Callable, Self

import pyperclip

from ...FzfPrompt import (
    Action,
    ActionsBuilder,
    Binding,
    ConflictResolution,
    EndStatus,
    PromptData,
    PromptEndingAction,
    ServerCall,
    ServerCallFunction,
    ShellCommand,
    Transform,
)
from ...FzfPrompt.constants import SHELL_COMMAND
from ...FzfPrompt.options.actions import BaseAction, ShellCommandActionType
from ...FzfPrompt.options.events import Hotkey, Situation
from .presets import (
    FILE_EDITORS,
    ChoicesGetter,
    FileEditor,
    ReloadChoices,
    Repeater,
    ShowInPreview,
    clip_current_preview,
    clip_options,
)


class OnEventBase[T, S](ABC):
    def __init__(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        if len(events) != len(set(events)):
            raise ValueError(f"Duplicate events for this mod: {events}")
        self._events: list[Hotkey | Situation] = list(events)
        self._on_conflict: ConflictResolution = on_conflict
        self._binding = Binding("")

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event in self._events:
            prompt_data.action_menu.add(event, self._binding, on_conflict=self._on_conflict)


class OnEvent[T, S](OnEventBase[T, S]):
    def run(self, name: str, *actions: Action) -> Self:
        self._binding += Binding(name, *actions)
        return self

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

    def run_transform(self, name: str, get_actions: ActionsBuilder[T, S], *base_actions: BaseAction) -> Self:
        return self.run(name, Transform(get_actions), *base_actions)

    def reload_choices(
        self,
        choices_getter: ChoicesGetter[T, S],
        name: str = "reload choices",
        *,
        sync: bool = False,
        repeat_interval: float | None = None,
        repeat_when: Callable[[PromptData[T, S]], bool] = lambda pd: True,
    ):
        name = f"{name}{' (sync)' if sync else ''}"
        if repeat_interval is None:
            return self.run(name, ReloadChoices(choices_getter, sync=sync))
        if repeat_interval < 0.2:
            raise ValueError("repeat_interval must be at least 0.2")
        return self.auto_repeat_run(
            name, ReloadChoices(choices_getter, sync=sync), repeat_interval=repeat_interval, repeat_when=repeat_when
        )

    def auto_repeat_run(
        self,
        name: str,
        *actions: Action,
        repeat_interval: float = 0.5,
        repeat_when: Callable[[PromptData[T, S]], bool] = lambda pd: True,
    ) -> Self:
        """❗Requires Options.listen()"""
        repeater = Repeater(*actions, repeat_interval=repeat_interval, repeat_when=repeat_when)
        return self.run_function(f"Every {repeat_interval:.2f}s {name}", repeater)

    def end_prompt(
        self,
        name: str,
        end_status: EndStatus,
        post_processor: Callable[[PromptData[T, S]], None] | None = None,
        *,
        allow_empty: bool = True,
    ):
        """Post-processor is called after the prompt has ended and before common post-processors are applied (defined in Mod.lastly)"""
        for event in self._events:
            self._binding += Binding(
                name, PromptEndingAction(end_status, event, post_processor, allow_empty=allow_empty)
            )

    # presets
    @property
    def accept(self):
        """Ends prompt with status 'accept'"""
        return self.end_prompt("accept", "accept")

    @property
    def accept_non_empty(self):
        """Ends prompt with status 'accept' if there are any selections"""
        return self.end_prompt("accept non-empty", "accept", allow_empty=False)

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

    def clip_current_preview_with_converter(self, converter: Callable[[str], str]):
        return self.run_function("clip current preview", lambda pd: clip_current_preview(pd, converter))

    @property
    def clip_options(self):
        return self.run_function("clip options", clip_options)

    @property
    def show_bindings_help_in_preview(self):
        self._binding += Binding(
            "Show bindings help in preview", ShowInPreview(lambda pd: pd.action_menu.get_bindings_help())
        ) | Binding("", "refresh-preview")
        return self

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

    @property
    def ring_bell(self):
        """Rings the terminal bell"""
        return self.run("ring bell", "bell")
