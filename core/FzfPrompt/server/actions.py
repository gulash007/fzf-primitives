from __future__ import annotations

import functools
import inspect
import json
import shlex
from typing import TYPE_CHECKING, Any, Callable, Concatenate, Self

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..action_menu.parametrized_actions import ShellCommand
from ..options import EndStatus, Hotkey, ShellCommandActionType, Situation
from ..shell import SHELL_SCRIPTS

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
        return f"{self.name}#{id(self.function)}"

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


class CommandOutput(str): ...


SOCKET_NUMBER_ENV_VAR = "FZF_PRIMITIVES_SOCKET_NUMBER"


class Request:
    def __init__(
        self, server_call_id: str, command_type: ShellCommandActionType, prompt_state: PromptState, kwargs: dict
    ):
        self.server_call_id = server_call_id
        self.command_type: ShellCommandActionType = command_type
        self.prompt_state = prompt_state
        self.kwargs = kwargs

    @staticmethod
    def create_command(server_call_id: str, function: ServerCallFunction, command_type: ShellCommandActionType) -> str:
        parameters = Request.parse_function_parameters(function)
        command = [
            f"{SHELL_SCRIPTS.make_server_call} {shlex.quote(server_call_id)} {command_type}",
            '{q} "{n}" {} "{+n}" "$(for x in {+}; do echo "$x"; done)"',  # making use of fzf placeholders
        ]
        for parameter in parameters:
            if isinstance(parameter.default, CommandOutput):
                # HACK: when default value of a parameter of ServerCallFunction is of type CommandOutput
                # then the parameter is going to be injected with the output of the value executed as shell command
                command.extend([parameter.name, f'"$({parameter.default} 2>&1)"'])
            else:
                # otherwise it's going to be injected with a shell variable of the same name (mainly env vars)
                command.extend([parameter.name, f'"${parameter.name}"'])
        socket_request_command = ["nc", "localhost", f'"${SOCKET_NUMBER_ENV_VAR}"']
        return f'{" ".join(command)} |& {" ".join(socket_request_command)}'

    @staticmethod
    def parse_function_parameters(function: ServerCallFunction) -> list[inspect.Parameter]:
        params = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
        if isinstance(function, functools.partial):
            if function.args:
                raise ValueError("Partial functions should only have passed keyworded arguments")
            params = list(filter(lambda p: p.name not in function.keywords, params))
        return params

    @classmethod
    def from_json(cls, data: dict) -> Self:
        prompt_state = PromptState.from_json(data["prompt_state"])
        return cls(data["server_call_id"], data["command_type"], prompt_state, data["kwargs"])


class PromptState:
    def __init__(
        self,
        query: str,
        single_index: int | None,
        indices: list[int],
        single_line: str | None,
        lines: list[str],
    ):
        self.query = query
        self.single_index = single_index
        self.indices = indices
        self.single_line = single_line
        self.lines = lines

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**data)

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)
