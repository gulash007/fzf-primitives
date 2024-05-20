from __future__ import annotations

import functools
import inspect
import json
import shlex
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from .actions import ServerCallFunction

SOCKET_NUMBER_ENV_VAR = "FZF_PRIMITIVES_SOCKET_NUMBER"
MAKE_SERVER_CALL_ENV_VAR_NAME = "FZF_PRIMITIVES_REQUEST_CREATING_SCRIPT"


class CommandOutput(str): ...


class Request:
    def __init__(self, server_call_id: str, prompt_state: PromptState | None, kwargs: dict):
        self.server_call_id = server_call_id
        self.prompt_state = prompt_state
        self.kwargs = kwargs

    @staticmethod
    def create_command(server_call_id: str, function: ServerCallFunction) -> str:
        parameters = Request.parse_function_parameters(function)
        command = [
            f'"${MAKE_SERVER_CALL_ENV_VAR_NAME}" "${SOCKET_NUMBER_ENV_VAR}" {shlex.quote(server_call_id)}',
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
    def parse_function_parameters(function: ServerCallFunction) -> list[inspect.Parameter]:
        params = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
        if isinstance(function, functools.partial):
            if function.args:
                raise ValueError("Partial functions should only have passed keyworded arguments")
            params = list(filter(lambda p: p.name not in function.keywords, params))
        return params

    @classmethod
    def from_json(cls, data: dict) -> Self:
        prompt_state = PromptState.from_json(data["prompt_state"]) if data["prompt_state"] else None
        return cls(data["server_call_id"], prompt_state, data["kwargs"])


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
