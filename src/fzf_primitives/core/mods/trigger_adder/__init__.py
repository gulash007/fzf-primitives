import functools
from typing import Protocol, overload

from ...FzfPrompt.action_menu import ConflictResolution
from ...FzfPrompt.options import Event, Hotkey
from ..on_trigger import OnTriggerBase
from .TriggerAdder import EventAdder, HotkeyAdder, TriggerAdder

__all__ = ["attach_hotkey_adder", "attach_event_adder", "attach_trigger_adder"]


class HotkeyAddingFunction[X, M: OnTriggerBase](Protocol):
    @staticmethod
    def __call__(self: X, hotkey: Hotkey, on_conflict: ConflictResolution = "raise error") -> M: ...  # type: ignore[reportSelfClsParameterName]


class EventAddingFunction[X, M: OnTriggerBase](Protocol):
    @staticmethod
    def __call__(self: X, event: Event, on_conflict: ConflictResolution = "raise error") -> M: ...  # type: ignore[reportSelfClsParameterName]


class TriggerAddingFunction[X, M: OnTriggerBase](Protocol):
    @staticmethod
    def __call__(self: X, trigger: Hotkey | Event, on_conflict: ConflictResolution = "raise error") -> M: ...  # type: ignore[reportSelfClsParameterName]


def attach_hotkey_adder[X, M: OnTriggerBase](func: HotkeyAddingFunction[X, M]):
    @overload
    def with_hotkey_adder(self: X, hotkey: Hotkey, on_conflict: ConflictResolution = "raise error") -> M: ...
    @overload
    def with_hotkey_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> HotkeyAdder[M]: ...
    def with_hotkey_adder(
        self: X, hotkey: Hotkey | None = None, on_conflict: ConflictResolution = "raise error"
    ) -> M | HotkeyAdder[M]:
        if hotkey:
            return func(self, hotkey, on_conflict=on_conflict)
        return HotkeyAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_hotkey_adder


def attach_event_adder[X, M: OnTriggerBase](func: EventAddingFunction[X, M]):
    @overload
    def with_event_adder(self: X, event: Event, on_conflict: ConflictResolution = "raise error") -> M: ...
    @overload
    def with_event_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> EventAdder[M]: ...
    def with_event_adder(
        self: X, event: Event | None = None, on_conflict: ConflictResolution = "raise error"
    ) -> M | EventAdder[M]:
        if event:
            return func(self, event, on_conflict=on_conflict)
        return EventAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_event_adder


def attach_trigger_adder[X, M: OnTriggerBase](func: TriggerAddingFunction[X, M]):
    @overload
    def with_trigger_adder(self: X, trigger: Hotkey | Event, on_conflict: ConflictResolution = "raise error") -> M: ...
    @overload
    def with_trigger_adder(self: X, *, on_conflict: ConflictResolution = "raise error") -> TriggerAdder[M]: ...
    def with_trigger_adder(
        self: X, trigger: Hotkey | Event | None = None, on_conflict: ConflictResolution = "raise error"
    ):
        if trigger:
            return func(self, trigger, on_conflict=on_conflict)
        return TriggerAdder[M](functools.partial(func, self, on_conflict=on_conflict))

    return with_trigger_adder
