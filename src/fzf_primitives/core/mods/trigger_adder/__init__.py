import functools
from typing import Protocol, overload

from ...FzfPrompt.action_menu import ConflictResolution
from ...FzfPrompt.options import Hotkey, Event
from ..on_trigger import OnTriggerBase
from .TriggerAdder import TriggerAdder, HotkeyAdder, EventAdder

__all__ = ["attach_hotkey_adder", "attach_event_adder", "attach_trigger_adder"]


class TriggerAddingFunction[X, T: (Hotkey, Event, Hotkey | Event), M: OnTriggerBase](Protocol):
    @staticmethod
    def __call__(self: X, *triggers: T, on_conflict: ConflictResolution = "raise error") -> M: ...


def attach_hotkey_adder[X, T: Hotkey, M: OnTriggerBase](func: TriggerAddingFunction[X, T, M]):
    @overload
    def with_hotkey_adder(
        self: X, hotkey: Hotkey, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> M: ...
    @overload
    def with_hotkey_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> HotkeyAdder[M]: ...
    def with_hotkey_adder(  # type: ignore # HACK: black magic
        self: X, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error"
    ) -> M | HotkeyAdder[M]:
        if hotkeys:
            return func(self, *hotkeys, on_conflict=on_conflict)
        return HotkeyAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_hotkey_adder


def attach_event_adder[X, T: Event, M: OnTriggerBase](func: TriggerAddingFunction[X, T, M]):
    @overload
    def with_event_adder(
        self: X, event: Event, *events: Event, on_conflict: ConflictResolution = "raise error"
    ) -> M: ...
    @overload
    def with_event_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> EventAdder[M]: ...
    def with_event_adder(  # type: ignore # HACK: black magic
        self: X, *events: Event, on_conflict: ConflictResolution = "raise error"
    ) -> M | EventAdder[M]:
        if events:
            return func(self, *events, on_conflict=on_conflict)
        return EventAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_event_adder


def attach_trigger_adder[X, T: (Hotkey | Event), M: OnTriggerBase](func: TriggerAddingFunction[X, T, M]):
    @overload
    def with_trigger_adder(self: X, trigger: T, *triggers: T, on_conflict: ConflictResolution = "raise error") -> M: ...
    @overload
    def with_trigger_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> TriggerAdder[M]: ...
    def with_trigger_adder(self: X, *triggers: T, on_conflict: ConflictResolution = "raise error"):  # type: ignore # HACK: black magic
        if triggers:
            return func(self, *triggers, on_conflict=on_conflict)
        return TriggerAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_trigger_adder
