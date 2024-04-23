from __future__ import annotations

from itertools import cycle
from pathlib import Path
from typing import Callable

from thingies import shell_command

from ..FzfPrompt import ConflictResolution, OnPreviewChange, Preview, PreviewFunction, PromptData
from ..FzfPrompt.options import Hotkey, Position, RelativeWindowSize
from ..monitoring import Logger


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


class FileViewer:
    def __init__(self, language: str = "python", theme: str = "Solarized (light)", *, plain: bool = True):
        self.language = language
        self.theme = theme
        self.plain = plain

    def view(self, *files: str | Path):
        if not files:
            return "No file selected"
        command = ["bat", "--color=always"]
        if self.language:
            command.extend(("--language", self.language))
        if self.theme:
            command.extend(("--theme", self.theme))
        if self.plain:
            command.append("--plain")
        command.append("--")  # Fixes file names starting with a hyphen
        command.extend(map(str, files))
        return shell_command(command)


class preview_preset:
    def __init__(
        self,
        name: str,
        command: str | PreviewFunction,
        on_change: OnPreviewChange | None = None,
        store_output: bool = True,
    ) -> None:
        self._name = name
        self._command = command
        self._on_change = on_change
        self._store_output = store_output

    def __get__(self, obj: PreviewMod, objtype=None):
        return obj.custom(self._name, self._command, self._on_change, self._store_output)


class PreviewMod[T, S]:

    def __init__(
        self,
        hotkey: Hotkey | None = None,
        window_size: int | RelativeWindowSize = "50%",
        window_position: Position = "right",
        label: str | None = None,
        *,
        conflict_resolution: ConflictResolution = "raise error",
        main: bool = False,
    ):
        self._preview_adder: Callable[[PromptData[T, S]]]
        self._hotkey: Hotkey | None = hotkey
        self._window_size: int | RelativeWindowSize = window_size
        self._window_position: Position = window_position
        self._label: str | None = label
        self._conflict_resolution: ConflictResolution = conflict_resolution
        self._main = main

    def custom(
        self,
        name: str,
        command: str | PreviewFunction[T, S],
        on_change: OnPreviewChange[T, S] | None = None,
        store_output: bool = True,
    ) -> None:
        self._preview_adder = lambda prompt_data: prompt_data.previewer.add(
            Preview[T, S](
                name,
                command,
                self._hotkey,
                on_change,
                self._window_size,
                self._window_position,
                self._label,
                store_output,
            ),
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

    def file(self, language: str = "python", theme: str = "Solarized (light)", plain: bool = True):
        """Parametrized preset for viewing files"""

        def view_file(prompt_data: PromptData[T, S]):
            if not (files := prompt_data.current_state.lines):
                return "No file selected"
            return FileViewer(language, theme, plain=plain).view(*files)

        self.custom("View File", view_file)

    def cycle(self, preview_functions: dict[str, PreviewFunction[T, S]], name: str = ""):
        preview_cycler = PreviewCycler(preview_functions)
        if not name:
            name = f'[{"|".join(preview_functions.keys())}]'
        preview = Preview(
            name,
            preview_cycler,
            self._hotkey,
            on_change=preview_cycler.next,
            window_size=self._window_size,
            window_position=self._window_position,
            label=self._label,
        )
        self._preview_adder = lambda prompt_data: prompt_data.previewer.add(
            preview, conflict_resolution=self._conflict_resolution, main=self._main
        )


class PreviewCycler:
    def __init__(self, preview_functions: dict[str, PreviewFunction]):
        self._preview_functions = preview_functions
        self._keys = cycle(preview_functions.keys())
        self._current_key: str
        self.logger = Logger.get_logger()

    def __call__(self, prompt_data: PromptData):
        return self._preview_functions[self._current_key](prompt_data)

    def next(self, prompt_data: PromptData, preview: Preview):
        if prompt_data.previewer.current_preview.id == preview.id:
            self._current_key = next(self._keys)
            self.logger.debug(f"Changing preview to next in cycle: {self._current_key}")
