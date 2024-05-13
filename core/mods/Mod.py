# Syntax sugar layer
from __future__ import annotations

from typing import Callable, Self

from ..FzfPrompt import Action, ConflictResolution, PromptData
from ..FzfPrompt.options import Hotkey, Options, Situation
from ..monitoring import LoggedComponent
from .event_adder import attach_hotkey_adder, attach_situation_adder
from .on_event import OnEvent
from .post_processing import PostProcessing
from .preview_mod import PreviewMod


class Mod[T, S](LoggedComponent):
    def __init__(self):
        super().__init__()
        self._mods: list[Callable[[PromptData], None]] = []
        self._options = Options()

    def apply(self, prompt_data: PromptData[T, S]):
        self.logger.info("---------- Applying mods ----------")
        try:
            for mod in self._mods:
                mod(prompt_data)
            prompt_data.options += self.options
        finally:
            self.clear()

    def clear(self):
        self._mods = []
        self._options = Options()

    # on event
    @attach_hotkey_adder
    def on_hotkey(self, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error") -> OnEvent[T, S]:
        return self.on_event(*hotkeys, on_conflict=on_conflict)

    @attach_situation_adder
    def on_situation(self, *situations: Situation, on_conflict: ConflictResolution = "raise error") -> OnEvent[T, S]:
        return self.on_event(*situations, on_conflict=on_conflict)

    def on_event(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        on_event_mod = OnEvent[T, S](*events, on_conflict=on_conflict)
        self._mods.append(on_event_mod)
        return on_event_mod

    # preview
    def preview(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error", main: bool = False):
        preview_mod = PreviewMod[T, S](*events, on_conflict=on_conflict, main=main)
        self._mods.append(preview_mod)
        return preview_mod

    # post processing
    @property
    def lastly(self) -> PostProcessing[T, S]:
        """Applied from left to right"""
        post_processing_mod = PostProcessing[T, S]()
        self._mods.append(post_processing_mod)
        return post_processing_mod

    # automations
    # TODO: custom (accepts function acting on PromptData)?
    def automate(self, *to_execute: Hotkey):
        self._mods.append(lambda pd: pd.automate(*to_execute))

    def automate_actions(self, *actions: Action):
        self._mods.append(lambda pd: pd.automate_actions(*actions))

    # other options
    @property
    def options(self) -> Options:
        return self._options

    # presets
    @property
    def default(self) -> Self:
        self.on_hotkey().CTRL_C.clip
        self.on_hotkey().CTRL_X.clip_current_preview
        self.on_hotkey().CTRL_Y.clip_options
        return self
