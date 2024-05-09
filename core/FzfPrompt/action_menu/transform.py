from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable

if TYPE_CHECKING:
    from . import Action
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..server import ServerCall
from .binding import Binding

type ActionsBuilder[T, S] = Callable[[PromptData[T, S]], Iterable[Action]]


class Transform[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, get_actions: ActionsBuilder[T, S], description: str | None = None) -> None:
        LoggedComponent.__init__(self)

        self.get_actions = get_actions
        super().__init__(self.get_transform_string, description or self._get_function_name(get_actions), "transform")

    def get_transform_string(self, prompt_data: PromptData[T, S]) -> str:
        binding = Binding(None, *self.get_actions(prompt_data))
        self.logger.debug(f"{self}: Created {binding}")
        prompt_data.server.add_server_calls(binding)
        return binding.to_action_string()

    def __str__(self) -> str:
        return f"[T]({self.id})"
