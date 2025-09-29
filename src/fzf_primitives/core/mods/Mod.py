# Syntax sugar layer
from __future__ import annotations

from typing import Callable, Self

from ..FzfPrompt import Action, ConflictResolution, PromptData
from ..FzfPrompt.options import Event, Hotkey, Options
from ..monitoring import LoggedComponent
from .on_trigger import OnTrigger
from .preview_mod import PreviewMod
from .trigger_adder import attach_event_adder, attach_hotkey_adder


class Mod[T, S](LoggedComponent):
    def __init__(self):
        super().__init__()
        self._mods: list[Callable[[PromptData], None]] = []
        self._options = Options()

    def apply(self, prompt_data: PromptData[T, S]):
        self.logger.info("---------- Applying mods ----------", trace_point="applying_mods")
        try:
            for mod in self._mods:
                mod(prompt_data)
            prompt_data.options += self.options
        finally:
            self.clear()

    def clear(self):
        self._mods = []
        self._options = Options()

    # on trigger
    @attach_hotkey_adder
    def on_hotkey(self, hotkey: Hotkey, on_conflict: ConflictResolution = "raise error") -> OnTrigger[T, S]:
        return self.on_trigger(hotkey, on_conflict=on_conflict)

    @attach_event_adder
    def on_event(self, event: Event, on_conflict: ConflictResolution = "raise error") -> OnTrigger[T, S]:
        return self.on_trigger(event, on_conflict=on_conflict)

    def on_trigger(self, trigger: Hotkey | Event, on_conflict: ConflictResolution = "raise error"):
        on_trigger_mod = OnTrigger[T, S](trigger, on_conflict=on_conflict)
        self._mods.append(on_trigger_mod)
        return on_trigger_mod

    # preview
    def preview(self, trigger: Hotkey | Event | None = None, on_conflict: ConflictResolution = "raise error", main: bool = False):
        preview_mod = PreviewMod[T, S](trigger, on_conflict=on_conflict, main=main)
        self._mods.append(preview_mod)
        return preview_mod

    # automations
    # TODO: custom (accepts function acting on PromptData)?
    def automate(self, *to_execute: Hotkey):
        """Currently can only automate hotkeys that have been explicitly bound"""
        self._mods.append(lambda pd: pd.automator.automate(*to_execute))

    def automate_actions(self, *actions: Action[T, S]):
        self._mods.append(lambda pd: pd.automator.automate_actions(*actions))

    # other options
    @property
    def options(self) -> Options:
        return self._options

    # presets
    def default(self) -> Self:
        """Some default useful preset"""
        self.on_hotkey().CTRL_C.clip
        self.on_hotkey().CTRL_X.clip_current_preview
        self.on_hotkey().CTRL_Y.clip_options
        return self
