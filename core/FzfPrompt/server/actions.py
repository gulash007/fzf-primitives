from __future__ import annotations

import functools
import inspect
import shlex
from typing import TYPE_CHECKING, Any, Callable, Concatenate, override

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..action_menu.parametrized_actions import ShellCommand
from ..options import EndStatus, Hotkey, ShellCommandActionType, Situation
from .request import ServerEndpoint

# means it requires first parameter to be of type PromptData but other parameters can be anything
type ServerCallFunctionGeneric[T, S, R] = Callable[Concatenate[PromptData[T, S], ...], R]
type ServerCallFunction[T, S] = ServerCallFunctionGeneric[T, S, Any]
SOCKET_NUMBER_ENV_VAR = "FZF_PRIMITIVES_SOCKET_NUMBER"
MAKE_SERVER_CALL_ENV_VAR_NAME = "FZF_PRIMITIVES_REQUEST_CREATING_SCRIPT"


class CommandOutput(str): ...


class ServerCall[T, S](ShellCommand):
    """❗ custom name mustn't have single nor double quotes in it. It only has informative purpose anyway"""

    def __init__(
        self,
        function: ServerCallFunction[T, S],
        description: str | None = None,
        command_type: ShellCommandActionType = "execute",
    ) -> None:
        self.name = description or f"f:{self._get_function_name(function)}"

        self.endpoint = ServerEndpoint(function, self.id)
        command = self._create_command(self.endpoint)
        super().__init__(command, command_type)

    @property
    def id(self) -> str:
        return f"{self.name}#{id(self)}"

    def _get_function_name(self, function: ServerCallFunction[T, S]) -> str:
        return function.__name__ if hasattr(function, "__name__") else str(function)

    @staticmethod
    def _create_command(server_endpoint: ServerEndpoint) -> str:
        parameters = ServerCall._parse_function_parameters(server_endpoint.function)
        command = [
            f'"${MAKE_SERVER_CALL_ENV_VAR_NAME}" "${SOCKET_NUMBER_ENV_VAR}" {shlex.quote(server_endpoint.id)}',
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
        return " ".join(command)

    @staticmethod
    def _parse_function_parameters(function: ServerCallFunction) -> list[inspect.Parameter]:
        params = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
        if isinstance(function, functools.partial):
            if function.args:
                raise ValueError("Partial functions should only have passed keyworded arguments")
            params = list(filter(lambda p: p.name not in function.keywords, params))
        return params

    def __str__(self) -> str:
        return f"[SC]{self.command_type}({self.endpoint.id})"


type PostProcessor[T, S] = Callable[[PromptData[T, S]], Any]


class PromptEndingAction[T, S](ServerCall, LoggedComponent):
    def __init__(
        self,
        end_status: EndStatus,
        event: Hotkey | Situation,
        post_processor: PostProcessor[T, S] | None = None,
        *,
        allow_empty: bool = True,
    ) -> None:
        LoggedComponent.__init__(self)
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self.event: Hotkey | Situation = event
        self.allow_empty = allow_empty
        super().__init__(self._pipe_results, command_type="execute-silent")

    def _pipe_results(self, prompt_data: PromptData[T, S]):
        if not self.allow_empty and not prompt_data.current_choices:
            return
        prompt_data.finish(self.event, self.end_status)
        self.logger.debug(f"Piping results:\n{prompt_data.result}")

    def __str__(self) -> str:
        return f"[PEA]({self.event},{self.end_status},{self._get_function_name(self.post_processor) if self.post_processor else None})"

    @override
    def action_string(self) -> str:
        return f"{super().action_string()}+{'accept' if self.allow_empty else 'accept-non-empty'}"
