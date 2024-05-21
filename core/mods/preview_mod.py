from __future__ import annotations

import itertools
from pathlib import Path
from typing import Iterable, Unpack

from ..FzfPrompt import (
    Binding,
    ConflictResolution,
    Preview,
    PreviewChangePreProcessor,
    PreviewFunction,
    PreviewMutationArgs,
    PreviewMutator,
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
    PreviewStyleMutationArgs,
)
from ..FzfPrompt.shell import shell_command
from ..monitoring import LoggedComponent
from .event_adder import attach_hotkey_adder, attach_situation_adder
from .on_event import OnEventBase


def preview_basic(prompt_data: PromptData):
    return str(prompt_data.current_state)


def get_fzf_json(prompt_data: PromptData, FZF_PORT: str):
    import json

    import requests

    return json.dumps(requests.get(f"http://127.0.0.1:{FZF_PORT}").json(), indent=2)


class FileViewer:
    def __init__(self, language: str = "", theme: str = "Solarized (light)", *, plain: bool = True):
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


class PreviewMod[T, S](OnEventBase[T, S], LoggedComponent):
    def __init__(
        self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error", main: bool = False
    ):
        super().__init__(*events, on_conflict=on_conflict)
        LoggedComponent.__init__(self)
        self._preview: Preview[T, S]
        self._specific_preview_mod: SpecificPreviewMod[T, S] | None = None
        self._main = main

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        try:
            preview = self._preview
        except AttributeError:
            self.logger.warning("PreviewMod has no effect as its Preview has not been set")
            return
        prompt_data.previewer.add(preview, main=self._main)
        for event in self._events:
            prompt_data.action_menu.add(event, preview.preview_change_binding, on_conflict=self._on_conflict)
        if self._specific_preview_mod:
            self._specific_preview_mod(prompt_data)

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
    ):
        self._preview = Preview[T, S](
            name,
            output_generator=output_generator,
            window_size=window_size,
            window_position=window_position,
            label=label,
            line_wrap=line_wrap,
            before_change_do=before_change_do,
            store_output=store_output,
        )
        self._specific_preview_mod = SpecificPreviewMod(self._preview)
        return self._specific_preview_mod

    # presets
    basic = preview_preset("basic", output_generator=preview_basic, label="PromptData.current_state")
    fzf_json = preview_preset("fzf json", output_generator=get_fzf_json, label="fzf JSON")

    def file(
        self,
        language: str = "",
        theme: str = "Solarized (light)",
        plain: bool = True,
        **kwargs: Unpack[PreviewStyleMutationArgs],
    ):
        """Parametrized preset for viewing files"""

        def view_file(prompt_data: PromptData[T, S]):
            if not (files := prompt_data.current_state.lines):
                return "No file selected"
            return FileViewer(language, theme, plain=plain).view(*files)

        return self.custom("View File", view_file, label="View file", **kwargs)

    # TODO: previews: dict[name, mutation args]
    def cycle_previews(self, previews: list[Preview[T, S]], name: str = ""):
        """If you don't need to separate Preview style specs (size, label, line wrap,…) for each preview, you can use cycle_functions"""
        if not name:
            name = f'[{"|".join(preview.name for preview in previews)}]'
        self._preview = CyclicalPreview(name, previews)


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


class SpecificPreviewMod[T, S]:
    def __init__(self, preview: Preview[T, S]):
        self._preview = preview
        self._mods: list[SpecificPreviewOnEvent] = []

    def __call__(self, prompt_data: PromptData[T, S]):
        try:
            for mod in self._mods:
                mod(prompt_data)
        finally:
            self.clear()

    def clear(self):
        self._mods = []

    @attach_hotkey_adder
    def on_hotkey(
        self, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> SpecificPreviewOnEvent[T, S]:
        return self.on_event(*hotkeys, on_conflict=on_conflict)

    @attach_situation_adder
    def on_situation(
        self, *situations: Situation, on_conflict: ConflictResolution = "raise error"
    ) -> SpecificPreviewOnEvent[T, S]:
        return self.on_event(*situations, on_conflict=on_conflict)

    def on_event(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        on_event_mod = SpecificPreviewOnEvent[T, S](*events, preview=self._preview, on_conflict=on_conflict)
        self._mods.append(on_event_mod)
        return on_event_mod


class SpecificPreviewOnEvent[T, S](OnEventBase[T, S]):
    def __init__(
        self, *events: Hotkey | Situation, preview: Preview[T, S], on_conflict: ConflictResolution = "raise error"
    ):
        super().__init__(*events, on_conflict=on_conflict)
        self._preview = preview
        self._binding = Binding("")
        self._initial_mutation = lambda pd: None

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for event in self._events:
            prompt_data.action_menu.add(event, self._binding, on_conflict=self._on_conflict)
        self._initial_mutation(prompt_data)

    def mutate(
        self,
        name: str,
        mutator: PreviewMutator[T, S],
        *,
        auto_apply_first: bool = False,
        mutate_only_when_already_focused: bool = True,
        focus_preview: bool = True,
    ) -> None:
        """This method can be called multiple times on the same PreviewMod object to add multiple mutators"""

        self._binding = Binding(
            name,
            Transform(
                lambda pd: (
                    ServerCall[T, S](
                        lambda pd: self._preview.update(**mutator(pd))
                        if pd.previewer.current_preview.id == self._preview.id or not mutate_only_when_already_focused
                        else None,
                        command_type="execute-silent",
                    ),
                    *(
                        self._preview.preview_change_binding.actions
                        if focus_preview or self._preview.id == pd.previewer.current_preview.id
                        else ()
                    ),
                )
            ),
        )
        if auto_apply_first:
            self._initial_mutation = lambda pd: self._preview.update(**mutator(pd))

    def cycle_mutators(
        self,
        name: str,
        mutators: Iterable[PreviewMutator[T, S]],
        auto_apply_first: bool = True,
        mutate_only_when_already_focused: bool = True,
        focus_preview: bool = True,
    ):
        mutators_cycle = itertools.cycle(mutators)
        get_next = lambda pd: next(mutators_cycle)(pd)
        self.mutate(
            name,
            get_next,
            auto_apply_first=auto_apply_first,
            mutate_only_when_already_focused=mutate_only_when_already_focused,
            focus_preview=focus_preview,
        )
