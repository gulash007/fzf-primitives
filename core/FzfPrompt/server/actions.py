from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Concatenate

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..action_menu.parametrized_actions import ShellCommand
from ..options import EndStatus, Hotkey, ShellCommandActionType, Situation
from .request import Request

# means it requires first parameter to be of type PromptData but other parameters can be anything
type ServerCallFunctionGeneric[T, S, R] = Callable[Concatenate[PromptData[T, S], ...], R]
type ServerCallFunction[T, S] = ServerCallFunctionGeneric[T, S, Any]


class ServerCall[T, S](ShellCommand):
    """❗ custom name mustn't have single nor double quotes in it. It only has informative purpose anyway"""

    def __init__(
        self,
        function: ServerCallFunction[T, S],
        description: str | None = None,
        command_type: ShellCommandActionType = "execute",
    ) -> None:
        self.function = function
        self.name = description or f"f:{self._get_function_name(function)}"

        command = Request.create_command(self.id, function, command_type)
        super().__init__(command, command_type)

    @property
    def id(self) -> str:
        return f"{self.name}#{id(self)}"

    def run(self, prompt_data: PromptData[T, S], request: Request) -> Any:
        prompt_data.set_current_state(request.prompt_state)
        return self.function(prompt_data, **request.kwargs)

    def _get_function_name(self, function: ServerCallFunction[T, S]) -> str:
        return function.__name__ if hasattr(function, "__name__") else str(function)

    def __str__(self) -> str:
        return f"[SC]{self.command_type}({self.id})"


type PostProcessor[T, S] = Callable[[PromptData[T, S]], Any]


class PromptEndingAction[T, S](ServerCall, LoggedComponent):
    def __init__(
        self, end_status: EndStatus, event: Hotkey | Situation, post_processor: PostProcessor[T, S] | None = None
    ) -> None:
        LoggedComponent.__init__(self)
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self.event: Hotkey | Situation = event
        super().__init__(self._pipe_results, command_type="execute-silent")

    def _pipe_results(self, prompt_data: PromptData[T, S]):
        prompt_data.finish(self.event, self.end_status)
        self.logger.debug(f"Piping results:\n{prompt_data.result}")

    def __str__(self) -> str:
        return f"[PEA]({self.event},{self.end_status},{self.post_processor.__name__ if self.post_processor else None})"
