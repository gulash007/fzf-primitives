from __future__ import annotations

from typing import Literal

from ...monitoring import LoggedComponent
from ..server import PromptEndingAction
from .parametrized_actions import Action, ParametrizedAction


class Binding(LoggedComponent):
    def __init__(self, name: str | None, /, *actions: Action):
        super().__init__()

        self.description = self._create_description(*actions)
        self.name = name or self.description  # name only has a descriptive function (appears in help and logs)
        self.actions: list[Action] = []
        self.final_action: PromptEndingAction | None = None
        for action in actions:
            if self.final_action is not None:
                raise ValueError(
                    f"Binding({self.name}): PromptEndingAction should be the last action in the binding: {self._create_description(*actions)}"
                )
            self.actions.append(action)
            if isinstance(action, PromptEndingAction):
                self.final_action = action

    def to_action_string(self) -> str:
        self.logger.debug(f"Turning binding to action string: {self.name}")
        actions = self.actions.copy()
        if self.final_action:
            actions.append("abort")
        action_strings = [
            action.action_string() if isinstance(action, ParametrizedAction) else action for action in actions
        ]
        return "+".join(action_strings)

    def __add__(self, other: Binding) -> Binding:
        name = " -> ".join(n for n in [self.name, other.name] if n)
        return Binding(name, *(self.actions + other.actions))

    def _create_description(self, *actions: Action) -> str:
        return "->".join([f"{str(action)}" for action in actions])

    def __str__(self) -> str:
        return self.description


ConflictResolution = Literal["raise error", "override", "append", "prepend"]


class BindingConflict(Exception):
    pass
