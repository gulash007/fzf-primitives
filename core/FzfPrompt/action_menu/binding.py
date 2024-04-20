from __future__ import annotations

from typing import Literal, Self

from ...monitoring import Logger
from ..server import PromptEndingAction
from .parametrized_actions import Action, ParametrizedAction

logger = Logger.get_logger()


class Binding:
    def __init__(self, name: str, /, *actions: Action):
        self.name = name  # only descriptive function
        self.actions: list[Action] = []
        self.final_action: PromptEndingAction | None = None
        for action in actions:
            if self.final_action is not None:
                raise ValueError(f"{self.name}: PromptEndingAction should be the last action in the binding: {actions}")
            self.actions.append(action)
            if isinstance(action, PromptEndingAction):
                self.final_action = action

    def to_action_string(self) -> str:
        actions = self.actions.copy()
        if self.final_action:
            actions.append("abort")
        action_strings = [
            action.action_string() if isinstance(action, ParametrizedAction) else action for action in actions
        ]
        return "+".join(action_strings)

    def __add__(self, other: Self) -> Self:
        return self.__class__(f"{self.name}+{other.name}", *(self.actions + other.actions))

    def __str__(self) -> str:
        actions = [f"'{str(action)}'" for action in self.actions]
        return f"{self.name}: {' -> '.join(actions)}"


ConflictResolution = Literal["raise error", "override", "append", "prepend"]


class BindingConflict(Exception):
    pass