from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable

if TYPE_CHECKING:
    from ..action_menu import Action
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..server import ServerCall
from .binding import Binding

type TransformationFunction[T, S] = Callable[[PromptData[T, S]], Iterable[Action]]


class Transformation[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, transformation_function: TransformationFunction[T, S]) -> None:
        LoggedComponent.__init__(self)
        name = f"Transformation ({transformation_function.__name__})"

        def get_transformation_string(prompt_data: PromptData[T, S]) -> str:
            self.logger.debug(name)
            binding = Binding(f"Created by {name}", *transformation_function(prompt_data))
            prompt_data.action_menu.add_server_calls(binding)
            return binding.to_action_string()

        super().__init__(get_transformation_string, name, "transform")
