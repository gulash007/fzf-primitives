from __future__ import annotations

import functools
import inspect
import json
import shlex
import socket
import traceback
from dataclasses import dataclass
from threading import Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Concatenate, ParamSpec, Self, TypeVar

if TYPE_CHECKING:
    from .prompt_data import PromptData
from ..monitoring import Logger
from .action_menu.parametrized_actions import ShellCommand
from .options import EndStatus, Hotkey, ShellCommandActionType, Situation
from .shell import SHELL_SCRIPTS

logger = Logger.get_logger()


class CommandOutput(str): ...


P = ParamSpec("P")
R = TypeVar("R", bound=str | None)
# means it requires first parameter to be of type PromptData but other parameters can be anything
type ServerCallFunctionGeneric[T, S, R] = Callable[Concatenate[PromptData[T, S], ...], R]
type ServerCallFunction[T, S] = ServerCallFunctionGeneric[T, S, Any]


class ServerCall[T, S](ShellCommand):
    """❗ custom name mustn't have single nor double quotes in it. It only has informative purpose anyway"""

    def __init__(
        self,
        function: ServerCallFunction[T, S],
        custom_name: str | None = None,
        command_type: ShellCommandActionType = "execute",
    ) -> None:
        self.function = function
        self.name = custom_name or function.__name__
        self.id = f"{self.name} ({id(self)})"

        command = Request.create_command(self.id, function, command_type)
        super().__init__(command, command_type)

    def __str__(self) -> str:
        return f"{self.id}: {super().__str__()}"

    def run(self, prompt_data: PromptData[T, S], request: Request) -> Any:
        prompt_data.set_current_state(request.prompt_state)
        return self.function(prompt_data, **request.kwargs)


type PostProcessor[T, S] = Callable[[PromptData[T, S]], Any]


class PromptEndingAction[T, S](ServerCall):
    def __init__(
        self, end_status: EndStatus, event: Hotkey | Situation, post_processor: PostProcessor[T, S] | None = None
    ) -> None:
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self.event: Hotkey | Situation = event
        super().__init__(self._pipe_results, command_type="execute-silent")

    def _pipe_results(self, prompt_data: PromptData[T, S]):
        prompt_data.finish(self.event, self.end_status)
        logger.debug(f"Piping results:\n{prompt_data.result}")

    def __str__(self) -> str:
        return f"{self.event}: end status '{self.end_status}' with {self.post_processor} post-processor: {super().__str__()}"


SOCKET_NUMBER_ENV_VAR = "FZF_PRIMITIVES_SOCKET_NUMBER"


@dataclass(frozen=True)
class Request:
    server_call_name: str
    command_type: ShellCommandActionType
    prompt_state: PromptState
    kwargs: dict

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
                command.extend([parameter.name, f'"$({parameter.default})"'])
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
        return cls(data["server_call_name"], data["command_type"], prompt_state, data["kwargs"])


@dataclass(frozen=True)
class PromptState:
    query: str
    single_index: int | None
    indices: list[int]
    single_line: str | None
    lines: list[str]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**data)


class Server[T, S](Thread):
    def __init__(
        self,
        prompt_data: PromptData[T, S],
        server_setup_finished: Event,
        server_should_close: Event,
    ) -> None:
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.server_setup_finished = server_setup_finished
        self.server_should_close = server_should_close
        self.server_calls: dict[str, ServerCall[T, S]] = {sc.id: sc for sc in prompt_data.action_menu.server_calls}
        self.socket_number: int

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("localhost", 0))
                socket_specs = server_socket.getsockname()
                self.socket_number = socket_specs[1]
                server_socket.listen()
                logger.info(f"Server listening on {socket_specs}...")

                self.server_setup_finished.set()
                server_socket.settimeout(0.05)
                while True:
                    try:
                        client_socket, addr = server_socket.accept()
                    except TimeoutError:
                        if self.server_should_close.is_set():
                            logger.info("Server closing")
                            break
                        continue
                    self._handle_request(client_socket, self.prompt_data)
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            self.server_setup_finished.set()

    def _handle_request(self, client_socket: socket.socket, prompt_data: PromptData[T, S]):
        payload_bytearray = bytearray()
        while r := client_socket.recv(1024):
            payload_bytearray.extend(r)
        payload = payload_bytearray.decode("utf-8").strip()
        try:
            request = Request.from_json(json.loads(payload))
            logger.debug(request.server_call_name)
            response = self.server_calls[request.server_call_name].run(prompt_data, request)
        except Exception as err:
            logger.error(trb := traceback.format_exc())
            payload_info = f"Payload contents:\n{payload}"
            logger.error(payload_info)
            response = f"{trb}\n{payload_info}"
            if isinstance(err, KeyError):
                response = f"{trb}\n{list(self.server_calls.keys())}"
                logger.error(f"Available server calls:\n{list(self.server_calls.keys())}")
            client_socket.sendall(str(response).encode("utf-8"))
        else:
            if response:
                client_socket.sendall(str(response).encode("utf-8"))
        finally:
            client_socket.close()
