from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..prompt_data import PromptData
    from .binding import Binding
from ...monitoring import Logger
from ..server import ServerCall

logger = Logger.get_logger()

type TransformationFunction[T, S] = Callable[[PromptData[T, S]], Binding]


class Transformation[T, S](ServerCall[T, S]):
    def __init__(self, transformation_function: TransformationFunction[T, S], custom_name: str | None = None) -> None:

        def get_transformation_string(prompt_data) -> str:
            logger.debug(f"Transformation: {self.name}")
            return transformation_function(prompt_data).to_action_string()

        super().__init__(get_transformation_string, custom_name, "transform")
