from __future__ import annotations

import shlex
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Thread
from typing import Callable, Literal, Self

import pyperclip

from fzf_primitives.core.monitoring import LoggedComponent

from ..FzfPrompt import (
    Action,
    ActionsBuilder,
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
    Transform,
)
from ..FzfPrompt.constants import SHELL_COMMAND
from ..FzfPrompt.options.actions import BaseAction, ShellCommandActionType
from ..FzfPrompt.options.events import Hotkey, Situation


class OnEventBase[T, S](ABC):
    def __init__(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        if len(events) != len(set(events)):
            raise ValueError(f"Duplicate events for this mod: {events}")
        self._events: list[Hotkey | Situation] = list(events)
        self._on_conflict: ConflictResolution = on_conflict

    @abstractmethod
    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        raise NotImplementedError


class OnEvent[T, S](OnEventBase[T, S]):
    def __init__(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        super().__init__(*events, on_conflict=on_conflict)
        self._binding = Binding("")

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event in self._events:
            prompt_data.add_binding(event, self._binding, on_conflict=self._on_conflict)

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
        self, choices_getter: ChoicesGetter[T, S], *, sync: bool = False, repeat_interval: float | None = None
    ):
        name = f"reload choices{' (sync)' if sync else ''}"
        if repeat_interval is None:
            return self.run(name, ReloadChoices(choices_getter, sync=sync))
        if repeat_interval < 0.2:
            raise ValueError("repeat_interval must be at least 0.2")
        return self.auto_repeat_run(name, ReloadChoices(choices_getter, sync=sync), repeat_interval=repeat_interval)

    def auto_repeat_run(self, name: str, *actions: Action, repeat_interval: float = 0.5) -> Self:
        thread = AutomatingThread(*actions, repeat_interval=repeat_interval)

        def repeat_http_action_request(prompt_data: PromptData, FZF_PORT: str):
            nonlocal thread
            prompt_data.action_menu.add_server_calls(Binding("", *actions))
            thread.set_port(FZF_PORT)
            if not thread.is_running:
                subprocess.Popen(
                    shlex.join(["curl", "-XPOST", f"localhost:{FZF_PORT}", "-d", "change-prompt(Auto-updating...> )"]),
                    shell=True,
                )
                thread.start()
                thread.is_running = True
            else:
                # TODO: reset prompt back to previous
                subprocess.Popen(
                    shlex.join(["curl", "-XPOST", f"localhost:{FZF_PORT}", "-d", "change-prompt(> )"]),
                    shell=True,
                )
                thread.should_stop = True
                thread = AutomatingThread(*actions, repeat_interval=repeat_interval)

        return self.run_function(f"Every {repeat_interval:.2f}s {name}", repeat_http_action_request)

    def end_prompt(
        self, name: str, end_status: EndStatus, post_processor: Callable[[PromptData[T, S]], None] | None = None
    ):
        """Post-processor is called after the prompt has ended and before common post-processors are applied (defined in Mod.lastly)"""
        for event in self._events:
            self._binding += Binding(name, PromptEndingAction(end_status, event, post_processor))

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


class AutomatingThread(Thread, LoggedComponent):
    def __init__(self, *actions: Action, repeat_interval: float = 0.5) -> None:
        super().__init__(daemon=True)
        LoggedComponent.__init__(self)
        self.is_running = False
        self.should_stop = False
        self.actions = actions
        self.repeat_interval = repeat_interval
        self.port: str

    def run(self) -> None:
        import subprocess
        import time

        while True:
            try:
                subprocess.Popen(
                    shlex.join(
                        [
                            "curl",
                            "-XPOST",
                            f"localhost:{self.port}",
                            "-d",
                            Binding("", *self.actions).to_action_string(),
                        ]
                    ),
                    shell=True,  # ❗ required for getting FZF_PORT
                )
                if self.should_stop:
                    break
            except Exception as err:
                self.logger.exception(err)
                continue
            finally:
                time.sleep(self.repeat_interval)

    def set_port(self, port: str):
        self.port = port
