from __future__ import annotations

from typing import Literal

from ...monitoring import LoggedComponent
from ..decorators import single_use_method
from ..options import Event, Hotkey, Options
from .binding import Binding
from .bindings_help import get_bindings_help
from .parametrized_actions import Action


# TODO: caching?
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Include fzf default --bind hotkeys (extra help)?
class ActionMenu[T, S](LoggedComponent):
    def __init__(self) -> None:
        super().__init__()
        self.bindings: dict[Hotkey | Event, Binding[T, S]] = {}

    @property
    def actions(self) -> list[Action[T, S]]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(self, trigger: Hotkey | Event, binding: Binding[T, S], *, on_conflict: ConflictResolution = "raise error"):
        self.logger.debug(
            f"🔗 Adding binding for '{trigger}': {binding} ({on_conflict} on conflict)",
            trace_point="adding_binding_to_action_menu",
            trigger=trigger,
            binding=binding.description,
        )
        if trigger not in self.bindings:
            self.bindings[trigger] = binding
        else:
            match on_conflict:
                case "raise error":
                    raise BindingConflict(f"Trigger {trigger} already has a binding: {self.bindings[trigger]}")
                case "override":
                    self.bindings[trigger] = binding
                case "append":
                    self.bindings[trigger] += binding
                case "prepend":
                    self.bindings[trigger] = binding + self.bindings[trigger]
                case "cycle with":
                    self.bindings[trigger] = self.bindings[trigger] | binding
                case _:
                    raise ValueError(f"Invalid conflict resolution: {on_conflict}")

    def get_bindings_help(self) -> str:
        return get_bindings_help(self)

    # TODO: silent binding (doesn't appear in header help)?
    @single_use_method
    def resolve_options(self) -> Options:
        options = Options()
        for trigger, binding in self.bindings.items():
            options.bind(trigger, binding.action_string())
        options.add_header(self.get_bindings_help()).header_first()
        return options


ConflictResolution = Literal["raise error", "override", "append", "prepend", "cycle with"]


class BindingConflict(Exception):
    pass
