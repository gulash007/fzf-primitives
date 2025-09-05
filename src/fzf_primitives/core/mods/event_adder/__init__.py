import functools
from typing import Protocol, overload

from ...FzfPrompt.action_menu import ConflictResolution
from ...FzfPrompt.options import Hotkey, Situation
from ..on_event import OnEventBase
from .EventAdder import EventAdder, HotkeyAdder, SituationAdder

__all__ = ["attach_hotkey_adder", "attach_situation_adder", "attach_event_adder"]


class EventAddingFunction[X, E: (Hotkey, Situation, Hotkey | Situation), M: OnEventBase](Protocol):
    @staticmethod
    def __call__(self: X, *events: E, on_conflict: ConflictResolution = "raise error") -> M: ...


def attach_hotkey_adder[X, E: Hotkey, M: OnEventBase](func: EventAddingFunction[X, E, M]):
    @overload
    def with_hotkey_adder(
        self: X, hotkey: Hotkey, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> M: ...
    @overload
    def with_hotkey_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> HotkeyAdder[M]: ...
    def with_hotkey_adder(
        self: X, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> M | HotkeyAdder[M]:
        if hotkeys:
            return func(self, *hotkeys, on_conflict=on_conflict)
        return HotkeyAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_hotkey_adder


def attach_situation_adder[X, E: Situation, M: OnEventBase](func: EventAddingFunction[X, E, M]):
    @overload
    def with_situation_adder(
        self: X, situation: Situation, *situations: Situation, on_conflict: ConflictResolution = "raise error"
    ) -> M: ...
    @overload
    def with_situation_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> SituationAdder[M]: ...
    def with_situation_adder(
        self: X, *situations: Situation, on_conflict: ConflictResolution = "raise error"
    ) -> M | SituationAdder[M]:
        if situations:
            return func(self, *situations, on_conflict=on_conflict)
        return SituationAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_situation_adder


def attach_event_adder[X, E: (Hotkey | Situation), M: OnEventBase](func: EventAddingFunction[X, E, M]):
    @overload
    def with_event_adder(self: X, event: E, *events: E, on_conflict: ConflictResolution = "raise error") -> M: ...
    @overload
    def with_event_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> EventAdder[M]: ...
    def with_event_adder(self: X, *events: E, on_conflict: ConflictResolution = "raise error"):
        if events:
            return func(self, *events, on_conflict=on_conflict)
        return EventAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_event_adder
