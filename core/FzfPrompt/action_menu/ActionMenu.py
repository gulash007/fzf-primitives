from __future__ import annotations

from ...monitoring import LoggedComponent
from ..decorators import single_use_method
from ..options import Hotkey, Options, Situation
from ..server import ServerCall
from .binding import Binding, BindingConflict, ConflictResolution
from .parametrized_actions import Action


# TODO: caching?
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Include fzf default --bind hotkeys (extra help)?
class ActionMenu[T, S](LoggedComponent):
    def __init__(self) -> None:
        super().__init__()
        self.bindings: dict[Hotkey | Situation, Binding] = {}
        self.server_calls: dict[str, ServerCall] = {}

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
                case _:
                    raise ValueError(f"Invalid conflict resolution: {on_conflict}")
        self.add_server_calls(binding)

    def add_server_calls(self, binding: Binding):
        for action in binding.actions:
            if isinstance(action, ServerCall):
                self.add_server_call(action)

    def add_server_call(self, server_call: ServerCall):
        if server_call.id not in self.server_calls:
            self.logger.debug(f"🤙 Adding server call: {server_call}")
            self.server_calls[server_call.id] = server_call

    # TODO: silent binding (doesn't appear in header help)?
    @single_use_method
    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.to_action_string())
        for event, binding in self.bindings.items():
            options.add_header(f"{event}\t{binding.name}")
        return options.header_first
