from __future__ import annotations

import inspect
import re
import socket
import traceback
from threading import Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Concatenate, ParamSpec, TypeVar

import pydantic

if TYPE_CHECKING:
    from .prompt_data import PromptData
from ..monitoring import Logger
from .action_menu.parametrized_actions import ShellCommand
from .decorators import single_use_method
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
        action_type: ShellCommandActionType = "execute",
    ) -> None:
        self.function = function
        self.name = custom_name or function.__name__
        self.id = f"{custom_name or function.__name__} ({id(self)})"

        template, placeholders_to_resolve = Request.create_template(self.id, function, action_type)
        super().__init__(template, action_type, placeholders_to_resolve)

    def __str__(self) -> str:
        return f"{self.id}: {super().__str__()}"


type PostProcessor[T, S] = Callable[[PromptData[T, S]], Any]


class PromptEndingAction[T, S](ServerCall):
    def __init__(self, end_status: EndStatus, post_processor: PostProcessor[T, S] | None = None) -> None:
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self._event: Hotkey | Situation | None = None
        # ❗ Needs to be silent, otherwise program can get stuck when waiting for user input on error in Server
        super().__init__(self.pipe_results, action_type="execute-silent")

    @property
    def event(self) -> Hotkey | Situation:
        if self._event is None:
            raise RuntimeError("event not resolved")
        return self._event

    def pipe_results(self, prompt_data: PromptData[T, S], event: Hotkey | Situation):
        prompt_data.finish(event, self.end_status)
        if self.post_processor:
            self.post_processor(prompt_data)
        logger.debug(f"Piping results:\n{prompt_data.result}")

    @single_use_method
    def resolve_event(self, event: Hotkey | Situation):
        self._event = event
        self.resolve(event=event)

    def __str__(self) -> str:
        event = self.event if self._event else "<event not resolved>"
        return f"{event}: end status '{self.end_status}' with {self.post_processor} post-processor: {super().__str__()}"


class Request(pydantic.BaseModel):
    server_call_name: str
    command_type: ShellCommandActionType
    prompt_state: PromptState
    kwargs: dict = {}

    @staticmethod
    def create_template(
        server_call_id: str, function: ServerCallFunction, command_type: ShellCommandActionType
    ) -> tuple[str, list[str]]:

        parameters = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
        jq_args = []
        placeholders_to_resolve = []
        for parameter in parameters:
            if isinstance(parameter.default, CommandOutput):
                jq_args.append(f'--arg {parameter.name} "$({parameter.default})"')
            else:
                # to be replaced using .resolve or is an environment variable
                jq_args.append(f'--arg {parameter.name} "${parameter.name}"')
                # environmental variables are recognized by being all uppercase
                if not re.match("^[A-Z_]*$", parameter.name):
                    placeholders_to_resolve.append(parameter.name)
        template = (
            PromptState.create_command()
            + " | jq --compact-output '{prompt_state:.} + {"
            + f'server_call_name:"{server_call_id}",command_type:"{command_type}"'
            + "} + {kwargs:$ARGS.named}' "
            + " ".join(jq_args)
            + " | nc localhost $SOCKET_NUMBER"
        )
        return template, placeholders_to_resolve


PLACEHOLDERS = {
    "query": "--arg query {q}",  # type str
    "index": "--argjson single_index $(x={n}; echo ${x:-null})",  # type int
    "fzf_selection": f'--argjson single_line "$({SHELL_SCRIPTS.selection_to_json} {{}})"',  # type str
    "indices": f'--argjson indices "$({SHELL_SCRIPTS.indices_to_json} {{+n}})"',  # type list[int]
    "lines": f'--argjson lines "$({SHELL_SCRIPTS.selections_to_json} {{+}})"',  # type list[str]
}


class PromptState(pydantic.BaseModel):
    query: str
    single_index: int | None
    indices: list[int]
    single_line: str | None
    lines: list[str]

    @staticmethod
    def create_command() -> str:
        return f'jq --null-input \'$ARGS.named\' {" ".join(PLACEHOLDERS.values())}'


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
                    self.handle_request(client_socket, self.prompt_data)
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            self.server_setup_finished.set()

    def handle_request(self, client_socket: socket.socket, prompt_data: PromptData[T, S]):
        payload_bytearray = bytearray()
        while r := client_socket.recv(1024):
            payload_bytearray.extend(r)
        payload = payload_bytearray.decode("utf-8").strip()
        try:
            request = Request.model_validate_json(payload)
            logger.debug(request.server_call_name)
            prompt_data.set_current_state(request.prompt_state)
            function = self.server_calls[request.server_call_name].function
            response = function(prompt_data, **request.kwargs)
        except Exception as err:
            logger.error(trb := traceback.format_exc())
            response = trb
            client_socket.sendall(str(response).encode("utf-8"))
            logger.error(f"Payload contents:\n{payload}")
        else:
            if response:
                client_socket.sendall(str(response).encode("utf-8"))
        finally:
            client_socket.close()
