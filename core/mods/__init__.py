# Syntax sugar layer
from __future__ import annotations

from typing import Callable, Self, overload

from ..FzfPrompt import Action, ConflictResolution, PromptData
from ..FzfPrompt.options import Hotkey, Options, Situation
from ..monitoring.Logger import get_logger
from .EventAdder import HotkeyAdder, SituationAdder
from .on_event import OnEvent
from .post_processing import PostProcessing
from .preview import PreviewMod

logger = get_logger()


class Mod[T, S]:
    def __init__(self, prompt_data: PromptData[T, S]):
        self._prompt_data = prompt_data
        self._mods: list[Callable[[PromptData], None]] = []
        self._options = Options()

    def apply(self):
        logger.info("---------- Applying mods ----------")
        try:
            for mod in self._mods:
                mod(self._prompt_data)
            self._prompt_data.options += self.options
        finally:
            self.clear()

    def clear(self):
        self._mods = []
        self._options = Options()

    @overload
    def on_hotkey(
        self, hotkey: Hotkey, *, conflict_resolution: ConflictResolution = "raise error"
    ) -> OnEvent[T, S]: ...
    @overload
    def on_hotkey(self, *, conflict_resolution: ConflictResolution = "raise error") -> HotkeyAdder[OnEvent[T, S]]: ...

    def on_hotkey(
        self, hotkey: Hotkey | None = None, *, conflict_resolution: ConflictResolution = "raise error"
    ) -> OnEvent[T, S] | HotkeyAdder[OnEvent[T, S]]:
        on_event_mod = OnEvent[T, S](conflict_resolution=conflict_resolution)
        self._mods.append(on_event_mod)
        if hotkey:
            on_event_mod.set_event(hotkey)
            return on_event_mod
        return HotkeyAdder(on_event_mod)

    @overload
    def on_situation(
        self, situation: Situation, *, conflict_resolution: ConflictResolution = "raise error"
    ) -> OnEvent[T, S]: ...
    @overload
    def on_situation(
        self, *, conflict_resolution: ConflictResolution = "raise error"
    ) -> SituationAdder[OnEvent[T, S]]: ...
    def on_situation(
        self, situation: Situation | None = None, *, conflict_resolution: ConflictResolution = "raise error"
    ) -> OnEvent[T, S] | SituationAdder[OnEvent[T, S]]:
        on_event_mod = OnEvent[T, S](conflict_resolution=conflict_resolution)
        self._mods.append(on_event_mod)
        if situation:
            on_event_mod.set_event(situation)
            return on_event_mod
        return SituationAdder(on_event_mod)

    def preview(
        self,
        hotkey: Hotkey | None = None,
        *,
        conflict_resolution: ConflictResolution = "raise error",
        main: bool = False,
    ):
        preview_mod = PreviewMod[T, S](hotkey, conflict_resolution=conflict_resolution, main=main)
        self._mods.append(preview_mod)
        return preview_mod

    @property
    def lastly(self) -> PostProcessing[T, S]:
        """Applied from left to right"""
        post_processing_mod = PostProcessing[T, S]()
        self._mods.append(post_processing_mod)
        return post_processing_mod

    @property
    def options(self) -> Options:
        return self._options

    # TODO: custom (accepts function acting on PromptData)?

    def automate(self, *to_execute: Hotkey):
        self._mods.append(lambda pd: pd.action_menu.automate(*to_execute))

    def automate_actions(self, *actions: Action):
        self._mods.append(lambda pd: pd.action_menu.automate_actions(*actions))

    # presets
    @property
    def default(self) -> Self:
        self.on_hotkey().CTRL_C.clip
        self.on_hotkey().CTRL_X.clip_current_preview
        self.on_hotkey().CTRL_Y.clip_options
        return self
