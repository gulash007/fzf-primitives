from __future__ import annotations

import itertools
from pathlib import Path
from typing import Callable, Iterable, Unpack

from ...FzfPrompt import (
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
from ...FzfPrompt.action_menu.transform import Transform
from ...FzfPrompt.options import Event, Hotkey, RelativeWindowSize, WindowPosition
from ...FzfPrompt.previewer.Preview import (
    DEFAULT_BEFORE_CHANGE_DO,
    DEFAULT_LABEL,
    DEFAULT_LINE_WRAP,
    DEFAULT_OUTPUT_GENERATOR,
    DEFAULT_STORE_OUTPUT,
    DEFAULT_WINDOW_POSITION,
    DEFAULT_WINDOW_SIZE,
    PreviewStyleMutationArgs,
)
from ...monitoring import LoggedComponent
from ..on_trigger import OnTriggerBase
from ..trigger_adder import attach_event_adder, attach_hotkey_adder
from .presets import CodeTheme, CyclicalPreview, FileViewer, get_fzf_env_vars, get_fzf_json, preview_basic


class preview_preset:
    def __init__(self, name: str, **kwargs: Unpack[PreviewMutationArgs]) -> None:
        self._name = name
        self._kwargs = kwargs

    def __get__(self, obj: PreviewMod, objtype=None):
        return obj.custom(self._name, **self._kwargs)


class PreviewMod[T, S](OnTriggerBase[T, S], LoggedComponent):
    def __init__(self, *triggers: Hotkey | Event, on_conflict: ConflictResolution = "raise error", main: bool = False):
        super().__init__(*triggers, on_conflict=on_conflict)
        LoggedComponent.__init__(self)
        self._preview: Preview[T, S]
        self._main = main
        self._additional_mods.append(lambda pd: pd.previewer.add(self._preview, main=self._main))

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        try:
            self._preview
        except AttributeError:
            self.logger.warning("PreviewMod has no effect as its Preview has not been set")
            return
        self.run_binding(self._preview.preview_change_binding)
        return super().__call__(prompt_data)

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
        self._additional_mods.append(specific_preview_mod := SpecificPreviewMod(self._preview))
        return specific_preview_mod

    # presets
    basic = preview_preset("basic", output_generator=preview_basic, label="PromptData state")
    fzf_json = preview_preset("fzf json", output_generator=get_fzf_json, label="fzf JSON")
    fzf_env_vars = preview_preset("fzf env vars", output_generator=get_fzf_env_vars, label="fzf env vars")

    def file(
        self,
        language: str = "",
        theme: CodeTheme = "dracula",
        plain: bool = True,
        converter: Callable[[T], str | Path] | None = None,
        **kwargs: Unpack[PreviewStyleMutationArgs],
    ):
        """Parametrized preset for viewing files"""

        def view_file(prompt_data: PromptData[T, S], FZF_PREVIEW_COLUMNS: str):
            converter_ = converter or prompt_data.converter
            if not (files := [converter_(f) for f in prompt_data.targets]):
                return "No file selected"
            return FileViewer(language, theme, plain=plain).view(*files, width=int(FZF_PREVIEW_COLUMNS))

        return self.custom("View File", view_file, label="View file", **kwargs)

    # TODO: previews: dict[name, mutation args]
    def cycle_previews(self, previews: list[Preview[T, S]], name: str = ""):
        """If you don't need to separate Preview style specs (size, label, line wrap,…) for each preview, you can use cycle_functions"""
        if not name:
            name = f"[{'|'.join(preview.name for preview in previews)}]"
        self._preview = CyclicalPreview(name, previews)


class SpecificPreviewMod[T, S]:
    def __init__(self, preview: Preview[T, S]):
        self._preview = preview
        self._mods: list[SpecificPreviewOnTrigger] = []

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
    ) -> SpecificPreviewOnTrigger[T, S]:
        return self.on_trigger(*hotkeys, on_conflict=on_conflict)

    @attach_event_adder
    def on_event(
        self, *events: Event, on_conflict: ConflictResolution = "raise error"
    ) -> SpecificPreviewOnTrigger[T, S]:
        return self.on_trigger(*events, on_conflict=on_conflict)

    def on_trigger(self, *triggers: Hotkey | Event, on_conflict: ConflictResolution = "raise error"):
        on_trigger_mod = SpecificPreviewOnTrigger[T, S](*triggers, preview=self._preview, on_conflict=on_conflict)
        self._mods.append(on_trigger_mod)
        return on_trigger_mod


class SpecificPreviewOnTrigger[T, S](OnTriggerBase[T, S]):
    def __init__(
        self, *triggers: Hotkey | Event, preview: Preview[T, S], on_conflict: ConflictResolution = "raise error"
    ):
        super().__init__(*triggers, on_conflict=on_conflict)
        self._preview = preview

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

        self.run_binding(
            Binding(
                f"[{self._preview.name}] {name}",
                Transform(
                    lambda pd: (
                        ServerCall[T, S](
                            lambda pd: self._preview.update(**mutator(pd))
                            if pd.previewer.current_preview.id == self._preview.id
                            or not mutate_only_when_already_focused
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
        )
        if auto_apply_first:
            self._additional_mods.append(lambda pd: self._preview.update(**mutator(pd)))

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
