from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..previewer import Previewer
from ...monitoring import Logger
from ..decorators import single_use_method
from ..options import Hotkey, Options, Situation
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
    def __init__(self, previewer: Previewer[T, S]) -> None:
        self.bindings: dict[Hotkey | Situation, Binding] = {}
        self.previewer = previewer
        self.to_automate: list[Binding | Hotkey] = []

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(
        self, event: Hotkey | Situation, binding: Binding, *, conflict_resolution: ConflictResolution = "raise error"
    ):
        if binding.final_action:
            binding.final_action.resolve_event(event)
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

    # TODO: silent binding (doesn't appear in header help)?
    @single_use_method
    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.to_action_string())
        header_help = "\n".join(f"{event}\t{action.name}" for event, action in self.bindings.items())
        if self.should_run_automator:
            options.listen()
        return options.header(header_help).header_first

    def automate(self, *to_automate: Binding | Hotkey):
        self.to_automate.extend(to_automate)

    def automate_actions(self, *actions: Action):
        self.automate(Binding("anonymous actions", *actions))

    @property
    def should_run_automator(self) -> bool:
        return bool(self.to_automate)