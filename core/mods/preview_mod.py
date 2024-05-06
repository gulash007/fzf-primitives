from __future__ import annotations

import itertools
from pathlib import Path
from typing import Callable, Unpack

from ..FzfPrompt import (
    Binding,
    ConflictResolution,
    Preview,
    PreviewChangePreProcessor,
    PreviewFunction,
    PreviewMutationArgs,
    PreviewMutator,
    PreviewStyleMutationArgs,
    PromptData,
    ServerCall,
)
from ..FzfPrompt.action_menu.transform import Transform
from ..FzfPrompt.options import Hotkey, RelativeWindowSize, Situation, WindowPosition
from ..FzfPrompt.previewer.Preview import (
    DEFAULT_BEFORE_CHANGE_DO,
    DEFAULT_LABEL,
    DEFAULT_LINE_WRAP,
    DEFAULT_OUTPUT_GENERATOR,
    DEFAULT_STORE_OUTPUT,
    DEFAULT_WINDOW_POSITION,
    DEFAULT_WINDOW_SIZE,
)
from ..FzfPrompt.shell import shell_command
from ..monitoring import LoggedComponent


def preview_basic(prompt_data: PromptData):
    return str(prompt_data.current_state)


def get_fzf_json(prompt_data: PromptData, FZF_PORT: str):
    import json

    import requests

    return json.dumps(requests.get(f"http://127.0.0.1:{FZF_PORT}").json(), indent=2)


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
    def __init__(self, name: str, **kwargs: Unpack[PreviewMutationArgs]) -> None:
        self._name = name
        self._kwargs = kwargs

    def __get__(self, obj: PreviewMod, objtype=None):
        return obj.custom(self._name, **self._kwargs)


class PreviewMod[T, S](LoggedComponent):
    def __init__(
        self,
        event: Hotkey | Situation | None = None,
        *,
        on_conflict: ConflictResolution = "raise error",
        main: bool = False,
    ):
        super().__init__()
        self._build_preview: Callable[[], Preview[T, S]]
        self._mutator_adders: list[Callable[[PromptData[T, S], Preview[T, S]], None]] = []
        self._event: Hotkey | Situation | None = event
        self._on_conflict: ConflictResolution = on_conflict
        self._main = main

    def custom(
        self,
        name: str,
        output_generator: str | PreviewFunction[T, S] = DEFAULT_OUTPUT_GENERATOR,
        window_size: int | RelativeWindowSize = DEFAULT_WINDOW_SIZE,
        window_position: WindowPosition = DEFAULT_WINDOW_POSITION,
        label: str = DEFAULT_LABEL,
        *,
        line_wrap: bool = DEFAULT_LINE_WRAP,
        before_change_do: PreviewChangePreProcessor[T, S] = DEFAULT_BEFORE_CHANGE_DO,
        store_output: bool = DEFAULT_STORE_OUTPUT,
    ) -> None:
        self._build_preview = lambda: Preview[T, S](
            name,
            output_generator=output_generator,
            window_size=window_size,
            window_position=window_position,
            label=label,
            line_wrap=line_wrap,
            before_change_do=before_change_do,
            store_output=store_output,
        )

    def mutate_preview(
        self,
        name: str,
        event: Hotkey | Situation,
        mutator: PreviewMutator[T, S],
        *,
        on_conflict: ConflictResolution = "raise error",
        mutate_only_when_already_focused: bool = True,
        focus_preview: bool = True,
    ) -> None:
        """This method can be called multiple times on the same PreviewMod object to add multiple mutators"""

        def add_preview_mutator(prompt_data: PromptData[T, S], preview: Preview[T, S]):
            binding = Binding(
                name,
                Transform(
                    lambda pd: (
                        ServerCall[T, S](
                            lambda pd: preview.update(**mutator(pd))
                            if pd.previewer.current_preview.id == preview.id or not mutate_only_when_already_focused
                            else None,
                            command_type="execute-silent",
                        ),
                        *(
                            preview.preview_change_binding.actions
                            if focus_preview or preview.id == pd.previewer.current_preview.id
                            else ()
                        ),
                    )
                ),
            )
            prompt_data.add_binding(event, binding, on_conflict=on_conflict)

        self._mutator_adders.append(add_preview_mutator)

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        try:
            preview = self._build_preview()
        except AttributeError:
            self.logger.warning("PreviewMod has no effect as its Preview has not been set")
            return
        prompt_data.add_preview(preview, self._event, on_conflict=self._on_conflict, main=self._main)
        for mutator_adder in self._mutator_adders:
            mutator_adder(prompt_data, preview)

    # presets
    basic = preview_preset("basic", output_generator=preview_basic, label="PromptData.current_state")
    fzf_json = preview_preset("fzf json", output_generator=get_fzf_json, label="fzf JSON")

    def file(self, language: str = "python", theme: str = "Solarized (light)", plain: bool = True):
        """Parametrized preset for viewing files"""

        def view_file(prompt_data: PromptData[T, S]):
            if not (files := prompt_data.current_state.lines):
                return "No file selected"
            return FileViewer(language, theme, plain=plain).view(*files)

        self.custom("View File", view_file)

    # TODO: previews: dict[name, mutation args]
    def cycle_previews(self, previews: list[Preview[T, S]], name: str = ""):
        """If you don't need to separate Preview style specs (size, label, line wrap,…) for each preview, you can use cycle_functions"""
        if not name:
            name = f'[{"|".join(preview.name for preview in previews)}]'
        self._build_preview = lambda: CyclicalPreview(name, previews)

    def cycle_functions(
        self,
        preview_functions: dict[str, PreviewFunction[T, S]],
        name: str = "",
        **style_args: Unpack[PreviewStyleMutationArgs],
    ):
        cyclical_preview_function = CyclicalPreviewFunction(preview_functions)
        if not name:
            name = f'[{"|".join(preview_functions.keys())}]'
        self.custom(name, cyclical_preview_function, before_change_do=cyclical_preview_function.next, **style_args)


# HACK: ❗This object pretends to be a preview but when transform is invoked it injects its previews cyclically
# into Previewer as current previews (it's never itself a current preview).
class CyclicalPreview[T, S](Preview[T, S], LoggedComponent):
    def __init__(self, name: str, previews: list[Preview[T, S]], event: Hotkey | Situation | None = None):
        LoggedComponent.__init__(self)
        super().__init__(name)
        self._previews = itertools.cycle(previews)
        self.preview_change_binding = Binding(name, Transform(self.next))
        self._current_preview = next(self._previews)

    def next(self, prompt_data: PromptData[T, S]):
        if self._current_preview.id == prompt_data.previewer.current_preview.id:
            self.logger.debug(f"Changing preview to next in cycle: {self._current_preview.name}")
            self._current_preview = next(self._previews)
        return self._current_preview.preview_change_binding.actions


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
        if not hasattr(self, "_current_key"):
            self._current_key = next(self._keys)
