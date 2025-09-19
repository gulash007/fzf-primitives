from __future__ import annotations

import itertools
from typing import Iterable, overload

from ...monitoring import LoggedComponent
from ..server import PromptEndingAction
from . import transform as t
from .parametrized_actions import Action, CompositeAction, ParametrizedAction


class Binding[T, S](LoggedComponent):
    @overload
    def __init__(self, name: None, /, *, action_groups: Iterable[ActionGroup[T, S]]): ...
    @overload
    def __init__(self, name: str | None, /, *actions: Action[T, S]): ...
    def __init__(
        self, name: str | None, /, *actions: Action[T, S], action_groups: Iterable[ActionGroup[T, S]] | None = None
    ):
        super().__init__()
        self._action_groups: dict[int, ActionGroup[T, S]] = {}
        if not action_groups:
            self._action_groups[ag.id] = (ag := ActionGroup(name, *actions))
        else:
            if actions:
                raise ValueError("Binding: Either pass action groups or actions, not both")
            if name:
                raise ValueError(
                    "Binding: When passing action groups, name should be None (it will be constructed from action group names)"
                )
            for action_group in action_groups:
                self._action_groups[action_group.id] = action_group
        self.actions: list[Action[T, S]]
        if len(self._action_groups) > 1:
            if any(ag.final_action for ag in self._action_groups.values()):
                raise NotImplementedError("Binding with multiple action groups can't have final action")
            action_groups_ids = itertools.cycle(self._action_groups.keys())
            self.actions = [t.Transform(lambda pd: self._action_groups[next(action_groups_ids)].actions, name)]
            self.final_action = None
        else:
            self.actions = (lone_action_group := list(self._action_groups.values())[0]).actions
            self.final_action = lone_action_group.final_action

    def action_string(self) -> str:
        actions = self.actions.copy()
        action_strings = [
            action.action_string() if isinstance(action, (ParametrizedAction, CompositeAction)) else action
            for action in actions
        ]
        return "+".join(action_strings)

    def __add__(self, other: Binding) -> Binding:
        """
        Has precedence over cycling: A + B | C + D == (A + B) | (C + D)
        Associative: (A + B) + C == A + (B + C)
        Distributive over cycling from left: A + (C | B) == A + C | A + B
        Distributive over cycling from right: (A | B) + C == A + C | B + C
        """
        # TODO: if both bindings have more than one action_group then raise error
        if len(self._action_groups) > 1 and len(other._action_groups) > 1:
            raise NotImplementedError("Cannot combine two bindings when both have multiple action groups")
        if len(self._action_groups) == 1 and len(other._action_groups) == 1:
            name = " -> ".join(n for n in (self.name, other.name) if n)
            return Binding(name, *(self.actions + other.actions))
        if len(self._action_groups) > 1:
            distributed_group = next(iter(other._action_groups.values()))
            return Binding(
                None,
                action_groups=[action_group + distributed_group for action_group in self._action_groups.values()],
            )
        else:
            distributed_group = next(iter(self._action_groups.values()))
            return Binding(
                None,
                action_groups=[distributed_group + action_group for action_group in other._action_groups.values()],
            )

    def __or__(self, other: Binding) -> Binding:
        """
        Has lower precedence to addition: A | B + C | D == A | (B + C) | D
        Associative: (A | B) | C == A | (B | C)
        """
        return Binding(None, action_groups=[*self._action_groups.values(), *other._action_groups.values()])

    @property
    def name(self) -> str:
        return " | ".join(group.name for group in self._action_groups.values())

    @property
    def description(self) -> str:
        return " | ".join(group.description for group in self._action_groups.values())

    def __str__(self) -> str:
        return self.description


class PromptEndingActionNotLast(ValueError):
    pass


# ❗ Not named ActionSequence because I'm not sure whether they actually will execute in sequence ('execute-silent' might be done in background, etc.)
class ActionGroup[T, S]:
    def __init__(self, name: str | None = None, *actions: Action[T, S]):
        self.id = id(self)
        self._actions: list[Action[T, S]] = []
        self.description = self._create_description(*actions)
        self.name = name or self.description
        self.final_action: PromptEndingAction[T, S] | None = None
        for action in actions:
            if self.final_action is not None:
                raise PromptEndingActionNotLast(self._create_description(*actions))
            self._actions.append(action)
            if isinstance(action, PromptEndingAction):
                self.final_action = action

    @property
    def actions(self) -> list[Action[T, S]]:
        return self._actions

    def _create_description(self, *actions: Action[T, S]) -> str:
        return "->".join([f"{str(action)}" for action in actions])

    def __add__(self, other: ActionGroup[T, S]) -> ActionGroup[T, S]:
        return ActionGroup(" -> ".join(n for n in (self.name, other.name) if n), *(self._actions + other._actions))
