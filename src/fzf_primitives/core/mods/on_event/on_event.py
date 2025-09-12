from __future__ import annotations

import subprocess
from abc import ABC
from pathlib import Path
from typing import Any, Callable, Self

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
from ...FzfPrompt.action_menu.parametrized_actions import MovePointer, ParametrizedAction
from ...FzfPrompt.constants import SHELL_COMMAND
from ...FzfPrompt.options.actions import BaseAction, ShellCommandActionType
from ...FzfPrompt.options.events import Hotkey, Situation
from .presets import (
    FILE_EDITORS,
    EntriesGetter,
    FileEditor,
    ReloadEntries,
    Repeater,
    SelectBy,
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
        self._additional_mods: list[Callable[[PromptData[T, S]], None]] = []

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event in self._events:
            prompt_data.action_menu.add(event, self._binding, on_conflict=self._on_conflict)
        for mod in self._additional_mods:
            mod(prompt_data)


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

    def select_by(self, name: str, predicate: Callable[[T], bool]) -> Self:
        """Selects items by the given predicate acting on an entry"""
        return self.run(name, SelectBy(predicate))

    def reload_entries(
        self,
        entries_getter: EntriesGetter[T, S],
        name: str = "reload entries",
        *,
        sync: bool = False,
        preserve_selections_by_key: Callable[[T], Any] | None = None,
        repeat_interval: float | None = None,
        repeat_when: Callable[[PromptData[T, S]], bool] = lambda pd: True,
    ):
        """
        Reload the entries list.

        Args:
            preserve_selections_by_key: Try to match previous selections with new entries on given predicate (usually some kind of equality).
            If not provided, all previous selections will be cleared after reload.
            repeat_interval: If provided, will auto-repeat the reload action every `repeat_interval` seconds. Must be at least 0.2.
        """
        name = f"{name}{' (sync)' if sync else ''}"

        if preserve_selections_by_key is not None:

            def save_selection_keys(pd: PromptData[T, S]):
                pd.run_vars["saved_selection_keys"] = {preserve_selections_by_key(item) for item in pd.selections}
                pd.run_vars["running_reload_and_preserve_selections"] = True

            self.run_function("save selections", save_selection_keys)

            def add_conditional_result_action(pd: PromptData[T, S]):
                def reselect_conditionally(pd: PromptData[T, S]):
                    if pd.run_vars.pop("running_reload_and_preserve_selections", None):
                        saved_keys = pd.run_vars.pop("saved_selection_keys", None)
                        if saved_keys is not None:
                            return [SelectBy[T, S](lambda item: preserve_selections_by_key(item) in saved_keys)]
                    return []

                pd.action_menu.add(
                    "result",
                    Binding(
                        "reselect if 'reload and preserve selections' was invoked", Transform(reselect_conditionally)
                    ),
                    on_conflict="append",
                )

            self._additional_mods.append(add_conditional_result_action)

        action = ReloadEntries(entries_getter, sync=sync)
        if repeat_interval is None:
            return self.run(name, action)
        if repeat_interval < 0.2:
            raise ValueError("repeat_interval must be at least 0.2")
        return self.auto_repeat_run(name, action, repeat_interval=repeat_interval, repeat_when=repeat_when)

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
    def clear_and_refocus(self):
        """clear query and move pointer to current entry"""

        def add_conditional_result_action(pd: PromptData[T, S]):
            def refocus_conditionally(pd: PromptData[T, S]):
                if pd.run_vars.pop("running_clear_and_refocus", None):
                    saved_index = pd.run_vars.pop("saved_current_index", None)
                    if saved_index is not None:
                        return [MovePointer(saved_index)]
                return []

            pd.action_menu.add(
                "result",
                Binding("refocus if 'clear and refocus' was invoked", Transform(refocus_conditionally)),
                on_conflict="append",
            )

        self._additional_mods.append(add_conditional_result_action)

        def save_current_index(pd: PromptData[T, S]):
            if pd.current_index is not None:
                pd.run_vars["saved_current_index"] = pd.current_index
                pd.run_vars["running_clear_and_refocus"] = True

        return self.run_function("clear and refocus", save_current_index, "clear-query", silent=True)

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
        file_getter = file_getter or (lambda pd: [pd.converter(f) for f in pd.targets])
        command = FILE_EDITORS[app]
        return self.run_function(f"open files in {app}", lambda pd: subprocess.run([command, "--", *file_getter(pd)]))

    @property
    def ring_bell(self):
        """Rings the terminal bell"""
        return self.run("ring bell", "bell")
