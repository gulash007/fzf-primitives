from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable, Concatenate, Iterable

if TYPE_CHECKING:
    from ..prompt_data import PromptData
    from . import Action
from ...monitoring import LoggedComponent
from ..server import PromptEndingAction, ServerCall, ServerCallFunction
from . import binding as b

type ActionsBuilder[T, S] = Callable[
    Concatenate[PromptData[T, S], ...], Iterable[Action[T, S] | ServerCallFunction[T, S]]
]


class Transform[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, get_actions: ActionsBuilder[T, S], description: str | None = None, *, bg: bool = False) -> None:
        """Hint: In get_actions, use 'bell' action as backup to errors so you can hear when an error happened"""
        LoggedComponent.__init__(self)

        self.get_actions = get_actions
        self._created_endpoints: list[str] = []
        super().__init__(
            self.getting_transform_string(get_actions),
            description or self._get_function_name(get_actions),
            "transform" if not bg else "bg-transform",
        )

    def getting_transform_string(self, actions_builder: ActionsBuilder[T, S]):
        @functools.wraps(actions_builder)
        def get_transform_string(prompt_data: PromptData[T, S], *args, **kwargs) -> str:
            actions: list[Action[T, S]] = [
                a.copy()
                if isinstance(a, ServerCall)
                else ServerCall(a, command_type="execute-silent")
                if callable(a)
                else a
                for a in actions_builder(prompt_data, *args, **kwargs)
            ]
            binding = b.Binding(None, *actions)
            self.logger.debug(f"{self}: Created {binding}", trace_point="transform_created", binding=binding.name)

            for server_call_id in self._created_endpoints:
                prompt_data.server.endpoints.pop(server_call_id, None)
            self._created_endpoints.clear()
            for action in binding.actions:
                if isinstance(action, ServerCall):
                    prompt_data.server.add_endpoint(action, prompt_data.trigger)
                    self._created_endpoints.append(action.id)
                    if isinstance(action, PromptEndingAction):
                        prompt_data.action_menu.add(prompt_data.trigger, b.Binding("", action), on_conflict="append")

            return binding.action_string()

        return get_transform_string

    def __str__(self) -> str:
        return f"[T]({self.id})"
