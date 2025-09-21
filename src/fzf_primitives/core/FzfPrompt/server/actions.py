from __future__ import annotations

import functools
import inspect
import shlex
from typing import TYPE_CHECKING, Any, Callable, Concatenate, Self, Type, override

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..action_menu.parametrized_actions import ShellCommand
from ..options import EndStatus, ShellCommandActionType
from .placeholders import CommandOutput, FzfPlaceholder, VarOutput

# means it requires first parameter to be of type PromptData but other parameters can be anything
type ServerCallFunctionGeneric[T, S, R] = Callable[Concatenate[PromptData[T, S], ...], R]
type ServerCallFunction[T, S] = ServerCallFunctionGeneric[T, S, Any]
SOCKET_NUMBER_ENV_VAR = "FZF_PRIMITIVES_SOCKET_NUMBER"
MAKE_SERVER_CALL_ENV_VAR_NAME = "FZF_PRIMITIVES_REQUEST_CREATING_SCRIPT"


class RemembersHowItWasConstructed[T](type):
    def __call__(cls: Type[T], *args, **kwargs) -> T:
        instance = super().__call__(*args, **kwargs)
        setattr(instance, "_new_copy", lambda: cls(*args, **kwargs))
        return instance


class ServerCall[T, S](ShellCommand[T, S], metaclass=RemembersHowItWasConstructed):
    """
    ❗ Don't reuse the same ServerCall instance in multiple bindings as created endpoints inherit .id but are
    also themselves parametrized by trigger so they're unique and ServerCall.id needs to find them
    """

    def __init__(
        self,
        function: ServerCallFunction[T, S],
        description: str | None = None,
        command_type: ShellCommandActionType = "execute",
    ) -> None:
        self.name = description or f"f:{self._get_function_name(function)}"
        self.function = function

        command = self._create_command(self.id, self.function)
        super().__init__(command, command_type)

    @property
    def id(self) -> str:
        return f"{self.name}#{id(self)}"

    def _get_function_name(self, function: ServerCallFunction[T, S]) -> str:
        return function.__name__ if hasattr(function, "__name__") else str(function)

    @staticmethod
    def _create_command(endpoint_id: str, function: ServerCallFunction) -> str:
        parameters = ServerCall._parse_function_parameters(function)
        command = [
            f'"${MAKE_SERVER_CALL_ENV_VAR_NAME}" "${SOCKET_NUMBER_ENV_VAR}" {shlex.quote(endpoint_id)}',
            '{q} {n} $FZF_SELECT_COUNT "{+n}"',  # making use of fzf placeholders and env vars
        ]
        for parameter in parameters:
            if isinstance(parameter.default, CommandOutput):
                command.extend([parameter.name, f'"$({parameter.default} 2>&1)"'])
            elif isinstance(parameter.default, VarOutput):
                command.extend([parameter.name, f'"${parameter.default}"'])
            elif isinstance(parameter.default, FzfPlaceholder):
                command.extend([parameter.name, parameter.default])
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
        return f"[SC]{self.command_type}({self.id})"

    def copy(self) -> Self:
        return getattr(self, "_new_copy")()


type PostProcessor[T, S] = Callable[[PromptData[T, S]], Any]


class PromptEndingAction[T, S](ServerCall, LoggedComponent):
    """end_status: Currently only used for control flow"""

    def __init__(
        self,
        end_status: EndStatus,
        post_processor: PostProcessor[T, S] | None = None,
        *,
        allow_empty: bool = True,
    ) -> None:
        LoggedComponent.__init__(self)
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self.allow_empty = allow_empty
        super().__init__(self._pipe_results, command_type="execute-silent")

    def _pipe_results(self, prompt_data: PromptData[T, S]):
        if not self.allow_empty and not prompt_data.targets:
            return
        prompt_data.finish(self.end_status)
        self.logger.trace("Piping results", trace_point="piping_results", result=prompt_data.result.to_dict())

    def __str__(self) -> str:
        return (
            f"[PEA]({self.end_status},{self._get_function_name(self.post_processor) if self.post_processor else None})"
        )

    @override
    def action_string(self) -> str:
        return f"{super().action_string()}+{'accept' if self.allow_empty else 'accept-non-empty'}"
