from __future__ import annotations

from typing import Callable

from thingies import shell_command

from ..FzfPrompt.options import Hotkey, Position, RelativeWindowSize
from ..FzfPrompt.Prompt import ConflictResolution, Preview, PreviewFunction, PromptData


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
        window_size: int | RelativeWindowSize = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ) -> None:
        self._name = name
        self._command = command
        self._window_size: int | RelativeWindowSize = window_size
        self._window_position: Position = window_position
        self._preview_label = preview_label
        self._store_output = store_output

    def __get__(self, obj: PreviewMod, objtype=None):
        return obj.custom(
            self._name, self._command, self._window_size, self._window_position, self._preview_label, self._store_output
        )


class PreviewMod[T, S]:

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
        window_size: int | RelativeWindowSize = "50%",
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
