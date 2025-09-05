from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Callable, Iterable

if TYPE_CHECKING:
    from ..prompt_data import PromptData
    from . import Action
from ...monitoring import LoggedComponent
from ..server import ServerCall
from . import binding as b

type ActionsBuilder[T, S] = Callable[[PromptData[T, S]], Iterable[Action]]


class Transform[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, get_actions: ActionsBuilder[T, S], description: str | None = None) -> None:
        LoggedComponent.__init__(self)

        self.get_actions = get_actions
        self._created_endpoints: list[str] = []
        super().__init__(self.get_transform_string, description or self._get_function_name(get_actions), "transform")

    def get_transform_string(self, prompt_data: PromptData[T, S]) -> str:
        binding = b.Binding(None, *self.get_actions(prompt_data))
        self.logger.debug(
            f"{self}: Created {binding}",
            trace_point="transform_created",
            binding=binding.name,
        )

        for server_call_id in self._created_endpoints:
            with contextlib.suppress(KeyError):
                prompt_data.server.endpoints.pop(server_call_id)
        self._created_endpoints.clear()
        for action in binding.actions:
            if isinstance(action, ServerCall):
                prompt_data.server.add_endpoint(action.endpoint)
                self._created_endpoints.append(action.endpoint.id)

        return binding.action_string()

    def __str__(self) -> str:
        return f"[T]({self.id})"
