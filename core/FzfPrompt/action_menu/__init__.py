from __future__ import annotations

from ...monitoring import Logger
from ..decorators import single_use_method
from ..options import Hotkey, Options, Situation
from ..server import ServerCall
from .binding import Binding, BindingConflict, ConflictResolution
from .parametrized_actions import Action, ParametrizedAction, ShellCommand

logger = Logger.get_logger()

__all__ = [
    "ActionMenu",
    "Binding",
    "BindingConflict",
    "ConflictResolution",
    "Action",
    "ParametrizedAction",
    "ShellCommand",
]

# TODO: caching?
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Include fzf default --bind hotkeys (extra help)?
# TODO: Show action menu as preview (to see hotkeys without restarting prompt); use preview(...)
# TODO: - How to invoke it through --bind and recreate the action back in the owner prompt?


class ActionMenu[T, S]:
    def __init__(self) -> None:
        self.bindings: dict[Hotkey | Situation, Binding] = {}
        self.server_calls: list[ServerCall] = []

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(
        self, event: Hotkey | Situation, binding: Binding, *, conflict_resolution: ConflictResolution = "raise error"
    ):
        logger.debug(f"🔗 Adding binding for '{event}': {binding} ({conflict_resolution} on conflict)")
        if event not in self.bindings:
            self.bindings[event] = binding
        else:
            match conflict_resolution:
                case "raise error":
                    raise BindingConflict(f"Event {event} already has a binding: {self.bindings[event]}")
                case "override":
                    self.bindings[event] = binding
                case "append":
                    self.bindings[event] += binding
                case "prepend":
                    self.bindings[event] = binding + self.bindings[event]
                case _:
                    raise ValueError(f"Invalid conflict resolution: {conflict_resolution}")
        for action in binding.actions:
            if isinstance(action, ServerCall):
                logger.debug(f"🤙 Adding server call: {action}")
                self.server_calls.append(action)

    # TODO: silent binding (doesn't appear in header help)?
    @single_use_method
    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.to_action_string())
        for event, binding in self.bindings.items():
            options.add_header(f"{event}\t{binding.name}")
        return options.header_first
