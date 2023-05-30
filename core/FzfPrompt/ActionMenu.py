from __future__ import annotations

from dataclasses import dataclass, field
from string import Template
from typing import TYPE_CHECKING, Any, Callable, Iterable, Literal, Self
from abc import ABC, abstractmethod

from .decorators import constructor

from .options import Event, Hotkey, Options


if TYPE_CHECKING:
    from .Prompt import Result
    from ..mods import Moddable, P
    from .PromptData import PromptData

# TODO: ❗ hotkey conflicts
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Allow multiselect (multioutput)?
# TODO: How to include --bind hotkeys (internal fzf prompt actions)? Maybe action menu can just serve as a hotkey hint
# Decorator to turn a function into a script that is then used with --bind 'hotkey:execute(python script/path {q} {+})'
# TODO: enter action in ActionMenu
# TODO: hotkeys only in ActionMenu prompt (not consumed in owner prompt)
# TODO: Instead of interpreting falsey values as reset, there should be an explicit named exception raised and caught
# TODO: Sort actions
# TODO: Show action menu as preview (to see hotkeys without restarting prompt)
# TODO: Make action_menu_hotkey owned by ActionMenu instead of prompt
# TODO: Will subclasses need more than just define actions? Maybe some more options can be overridden?
# TODO: Preview of result
# TODO: ❗ Remake as an hotkey:execute(action_menu_prompt <prompt id (port #)>)
# TODO: - How to invoke it through --bind and recreate the action back in the owner prompt?
# TODO: Show command in fzf prompt (invoke using a hotkey maybe?)
# TODO: replace_prompt: bool = False
# TODO: silent: bool = True


class ShellCommand:
    def __init__(self, value: str) -> None:
        self.value = value

    # TODO: check finalization for easier testing
    def safe_substitute(self, mapping: dict) -> None:
        """replaces $key present in .command with value"""
        self.value = Template(self.value).safe_substitute(mapping)

    def __str__(self) -> str:
        return self.value


class ParametrizedAction(ABC):
    @abstractmethod
    def __str__(self) -> str:
        """To resolve into fzf options"""


class PostProcessAction:
    """Requires program to know what event happened (what hotkey was pressed)"""

    def __init__(self, result_processor: Callable[[Result], Any]) -> None:
        self.result_processor = result_processor


class ActionAdder:
    """Does the same thing as a property. It exists to shorten code."""

    def __init__(self, *actions: Action):
        self._actions = actions

    def __get__(self, obj: Binding, objtype: type[Binding] | None = None) -> Binding:
        return obj.add(*self._actions)


class Binding:
    toggle_all = ActionAdder("toggle-all")

    def __init__(self, name, *actions: Action):
        self.name = name
        self.actions: list[Action] = list(actions)

    def add(self, *actions: Action) -> Self:
        self.actions.extend(actions)
        return self


class ActionMenu:
    def __init__(self) -> None:
        self.bindings: dict[Hotkey | Event, Binding] = {}
        self.post_processors: dict[Hotkey | Event, Callable[[Result], Any]] = {}

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(self, name: str, event: Hotkey | Event, *actions: Action):
        if event in self.bindings:
            raise RuntimeError(f"Hotkey conflict ({event}): {name} vs {self.bindings[event].name}")
        self.bindings[event] = Binding(name, *actions)
        for action in actions:
            if isinstance(action, PostProcessAction):
                self.post_processors[event] = action.result_processor

    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(
                event,
                "+".join(
                    f"execute({action})" if isinstance(action, ShellCommand) else str(action)
                    for action in binding.actions
                ),
            )
        header_help = "\n".join(f"{event}\t{action.name}" for event, action in self.bindings.items())
        return options.header(header_help).header_first

    def process_result(self, result: Result):
        post_processor = self.post_processors.get(result.hotkey) if result.hotkey else None
        return post_processor(result) if post_processor else result


BaseAction = Literal[
    "accept",
    "toggle-all",
    "select-all",
    "refresh-preview",
]
Action = BaseAction | ParametrizedAction | PostProcessAction | ShellCommand
