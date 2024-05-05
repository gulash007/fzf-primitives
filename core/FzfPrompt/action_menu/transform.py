from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable

if TYPE_CHECKING:
    from . import Action
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..server import ServerCall
from .binding import Binding

type TransformFunction[T, S] = Callable[[PromptData[T, S]], Iterable[Action]]


class Transform[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, transform_function: TransformFunction[T, S]) -> None:
        LoggedComponent.__init__(self)
        name = f"Transform ({transform_function.__name__})"

        def get_transform_string(prompt_data: PromptData[T, S]) -> str:
            binding = Binding(f"Created by {name}", *transform_function(prompt_data))
            prompt_data.action_menu.add_server_calls(binding)
            action_string = binding.to_action_string()
            self.logger.debug(f"Transform: {action_string}")
            return action_string

        super().__init__(get_transform_string, name, "transform")
