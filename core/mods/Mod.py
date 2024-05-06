# Syntax sugar layer
from __future__ import annotations

import functools
from typing import Callable, Self, overload

from ..FzfPrompt import Action, ConflictResolution, PromptData
from ..FzfPrompt.options import Hotkey, Options, WindowPosition, RelativeWindowSize, Situation
from ..monitoring import LoggedComponent
from .EventAdder import HotkeyAdder, SituationAdder
from .on_event import OnEvent
from .post_processing import PostProcessing
from .preview_mod import PreviewMod


class Mod[T, S](LoggedComponent):
    def __init__(self, prompt_data: PromptData[T, S]):
        super().__init__()
        self._prompt_data = prompt_data
        self._mods: list[Callable[[PromptData], None]] = []
        self._options = Options()

    def apply(self):
        self.logger.info("---------- Applying mods ----------")
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
        self, hotkey: Hotkey, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> OnEvent[T, S]: ...
    @overload
    def on_hotkey(self, *, on_conflict: ConflictResolution = "raise error") -> HotkeyAdder[OnEvent[T, S]]: ...

    def on_hotkey(
        self, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> OnEvent[T, S] | HotkeyAdder[OnEvent[T, S]]:
        if hotkeys:
            return self.on_event(*hotkeys, on_conflict=on_conflict)
        return HotkeyAdder(functools.partial(self.on_hotkey, on_conflict=on_conflict))

    @overload
    def on_situation(
        self, situation: Situation, *situations: Situation, on_conflict: ConflictResolution = "raise error"
    ) -> OnEvent[T, S]: ...
    @overload
    def on_situation(self, *, on_conflict: ConflictResolution = "raise error") -> SituationAdder[OnEvent[T, S]]: ...
    def on_situation(
        self, *situations: Situation, on_conflict: ConflictResolution = "raise error"
    ) -> OnEvent[T, S] | SituationAdder[OnEvent[T, S]]:
        if situations:
            return self.on_event(*situations, on_conflict=on_conflict)
        return SituationAdder(functools.partial(self.on_situation, on_conflict=on_conflict))

    def on_event(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        on_event_mod = OnEvent[T, S](*events, on_conflict=on_conflict)
        self._mods.append(on_event_mod)
        return on_event_mod

    def preview(
        self,
        event: Hotkey | Situation | None = None,
        *,
        on_conflict: ConflictResolution = "raise error",
        main: bool = False,
    ):
        preview_mod = PreviewMod[T, S](event, on_conflict=on_conflict, main=main)
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
        self._mods.append(lambda pd: pd.automate(*to_execute))

    def automate_actions(self, *actions: Action):
        self._mods.append(lambda pd: pd.automate_actions(*actions))

    # presets
    @property
    def default(self) -> Self:
        self.on_hotkey().CTRL_C.clip
        self.on_hotkey().CTRL_X.clip_current_preview
        self.on_hotkey().CTRL_Y.clip_options
        return self
