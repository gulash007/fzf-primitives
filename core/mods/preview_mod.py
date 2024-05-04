from __future__ import annotations

import itertools
from pathlib import Path
from typing import Callable

from ..FzfPrompt import (
    Binding,
    ConflictResolution,
    Preview,
    PreviewChangePreProcessor,
    PreviewFunction,
    PreviewMutator,
    PromptData,
    ServerCall,
)
from ..FzfPrompt.action_menu.transformation import Transformation
from ..FzfPrompt.options import Hotkey, WindowPosition, RelativeWindowSize, Situation
from ..FzfPrompt.shell import shell_command
from ..monitoring import LoggedComponent


def preview_basic(prompt_data: PromptData):
    return str(prompt_data.current_state)


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
        output_generator: str | PreviewFunction,
        before_change_do: PreviewChangePreProcessor | None = None,
        store_output: bool = True,
    ) -> None:
        self._name = name
        self._output_generator = output_generator
        self._before_change_do = before_change_do
        self._store_output = store_output

    def __get__(self, obj: PreviewMod, objtype=None):
        return obj.custom(self._name, self._output_generator, self._before_change_do, self._store_output)


class PreviewMod[T, S](LoggedComponent):
    def __init__(
        self,
        event: Hotkey | Situation | None = None,
        window_size: int | RelativeWindowSize = "50%",
        window_position: WindowPosition = "right",
        label: str = "",
        *,
        line_wrap: bool = True,
        conflict_resolution: ConflictResolution = "raise error",
        main: bool = False,
    ):
        super().__init__()
        self._build_preview: Callable[[], Preview[T, S]]
        self._mutator_adders: list[Callable[[PromptData[T, S], Preview[T, S]], None]] = []
        self._event: Hotkey | Situation | None = event
        self._window_size: int | RelativeWindowSize = window_size
        self._window_position: WindowPosition = window_position
        self._label = label
        self._line_wrap = line_wrap
        self._conflict_resolution: ConflictResolution = conflict_resolution
        self._main = main

    def custom(
        self,
        name: str,
        output_generator: str | PreviewFunction[T, S],
        before_change_do: PreviewChangePreProcessor[T, S] | None = None,
        store_output: bool = True,
    ) -> None:
        self._build_preview = lambda: Preview[T, S](
            name,
            output_generator,
            self._window_size,
            self._window_position,
            self._label,
            before_change_do,
            line_wrap=self._line_wrap,
            store_output=store_output,
        )

    def mutate_preview(
        self,
        name: str,
        event: Hotkey | Situation,
        mutator: PreviewMutator[T, S],
        *,
        conflict_resolution: ConflictResolution = "raise error",
        mutate_only_when_already_focused: bool = True,
    ) -> None:
        """This method can be called multiple times on the same PreviewMod object to add multiple mutators"""

        def add_preview_mutator(prompt_data: PromptData[T, S], preview: Preview[T, S]):
            binding = Binding(
                name,
                ServerCall[T, S](
                    lambda pd: None
                    if pd.previewer.current_preview.id != preview.id and mutate_only_when_already_focused
                    else preview.update(**mutator(pd)),
                    command_type="execute-silent",
                ),
                *preview.preview_change_binding.actions,
            )
            prompt_data.action_menu.add(event, binding, conflict_resolution=conflict_resolution)

        self._mutator_adders.append(add_preview_mutator)

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        try:
            preview = self._build_preview()
        except AttributeError:
            self.logger.warning("PreviewMod has no effect as its Preview has not been set")
            return
        prompt_data.previewer.add(preview, self._event, conflict_resolution=self._conflict_resolution, main=self._main)
        for mutator_adder in self._mutator_adders:
            mutator_adder(prompt_data, preview)

    # presets
    basic = preview_preset("basic", preview_basic)

    def file(self, language: str = "python", theme: str = "Solarized (light)", plain: bool = True):
        """Parametrized preset for viewing files"""

        def view_file(prompt_data: PromptData[T, S]):
            if not (files := prompt_data.current_state.lines):
                return "No file selected"
            return FileViewer(language, theme, plain=plain).view(*files)

        self.custom("View File", view_file)

    def cycle_previews(self, previews: list[Preview[T, S]], name: str = ""):
        """If you don't need to separate Preview style specs (size, label, line wrap,…) for each preview, you can use cycle_functions"""
        if not name:
            name = f'[{"|".join(preview.name for preview in previews)}]'
        self._build_preview = lambda: CyclicalPreview(name, previews)

    def cycle_functions(self, preview_functions: dict[str, PreviewFunction[T, S]], name: str = ""):
        cyclical_preview_function = CyclicalPreviewFunction(preview_functions)
        if not name:
            name = f'[{"|".join(preview_functions.keys())}]'
        self.custom(name, cyclical_preview_function, cyclical_preview_function.next)


# HACK: ❗This object pretends to be a preview but when transformation is invoked it injects its previews cyclically
# into Previewer as current previews (it's never itself a current preview).
class CyclicalPreview[T, S](Preview[T, S], LoggedComponent):
    def __init__(self, name: str, previews: list[Preview[T, S]], event: Hotkey | Situation | None = None):
        LoggedComponent.__init__(self)
        super().__init__(name, "")
        self._previews = itertools.cycle(previews)
        self.preview_change_binding = Binding(name, Transformation(self.next))
        self._current_preview = next(self._previews)

    def next(self, prompt_data: PromptData[T, S]) -> Binding:
        if self._current_preview.id == prompt_data.previewer.current_preview.id:
            self.logger.debug(f"Changing preview to next in cycle: {self._current_preview.name}")
            self._current_preview = next(self._previews)
        return self._current_preview.preview_change_binding


class CyclicalPreviewFunction(LoggedComponent):
    def __init__(self, preview_functions: dict[str, PreviewFunction]):
        super().__init__()
        self._preview_functions = preview_functions
        self._keys = itertools.cycle(preview_functions.keys())
        self._current_key: str

    def __call__(self, prompt_data: PromptData):
        return self._preview_functions[self._current_key](prompt_data)

    def next(self, prompt_data: PromptData, preview: Preview):
        if prompt_data.previewer.current_preview.id == preview.id:
            self._current_key = next(self._keys)
            self.logger.debug(f"Changing preview to next in cycle: {self._current_key}")
