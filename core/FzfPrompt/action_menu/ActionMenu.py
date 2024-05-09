from __future__ import annotations

from typing import Literal

from ...monitoring import LoggedComponent
from ..decorators import single_use_method
from ..options import Hotkey, Options, Situation
from .binding import Binding
from .parametrized_actions import Action


# TODO: caching?
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Include fzf default --bind hotkeys (extra help)?
class ActionMenu[T, S](LoggedComponent):
    def __init__(self) -> None:
        super().__init__()
        self.bindings: dict[Hotkey | Situation, Binding] = {}

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(self, event: Hotkey | Situation, binding: Binding, *, on_conflict: ConflictResolution = "raise error"):
        self.logger.debug(f"🔗 Adding binding for '{event}': {binding} ({on_conflict} on conflict)")
        if event not in self.bindings:
            self.bindings[event] = binding
        else:
            match on_conflict:
                case "raise error":
                    raise BindingConflict(f"Event {event} already has a binding: {self.bindings[event]}")
                case "override":
                    self.bindings[event] = binding
                case "append":
                    self.bindings[event] += binding
                case "prepend":
                    self.bindings[event] = binding + self.bindings[event]
                case "cycle with":
                    self.bindings[event] = self.bindings[event] | binding
                case _:
                    raise ValueError(f"Invalid conflict resolution: {on_conflict}")

    # TODO: silent binding (doesn't appear in header help)?
    @single_use_method
    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.action_string())
        for event, binding in self.bindings.items():
            options.add_header(f"{event}\t{binding.name}")
        return options.header_first


ConflictResolution = Literal["raise error", "override", "append", "prepend", "cycle with"]


class BindingConflict(Exception):
    pass
