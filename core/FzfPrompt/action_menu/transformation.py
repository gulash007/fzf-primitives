from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..prompt_data import PromptData
    from .binding import Binding
from ...monitoring import LoggedComponent
from ..server import ServerCall

type TransformationFunction[T, S] = Callable[[PromptData[T, S]], Binding]


class Transformation[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, transformation_function: TransformationFunction[T, S], custom_name: str | None = None) -> None:
        LoggedComponent.__init__(self)

        def get_transformation_string(prompt_data) -> str:
            self.logger.debug(f"Transformation: {self.name}")
            return transformation_function(prompt_data).to_action_string()

        super().__init__(get_transformation_string, custom_name, "transform")
