# Black magic layer
from __future__ import annotations

import inspect
import socket
import traceback
from dataclasses import dataclass
from string import Template
from threading import Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Literal, Protocol, Self

import pydantic

from ..monitoring.Logger import get_logger

from ..actions.functions import preview_basic
from .ActionMenu import ShellCommand
from .commands.fzf_placeholders import PLACEHOLDERS
from .options import Hotkey, Options

if TYPE_CHECKING:
    from ..mods import Moddable, P
    from .Previewer import Preview
    from .PromptData import PromptData

logger = get_logger()

# class ServerFunction(Protocol):
#     @staticmethod
#     def __call__(prompt_data: PromptData) -> str:
#         ...


# def update_prompt_data(prompt_data: PromptData, query: str, *selections: str):
#     prompt_data.update(query, selections)
#     # print("Updated to:", prompt_data)
#     return f"Updated prompt data: {prompt_data}"


# def get_prompt_data(prompt_data: PromptData):
#     return str(prompt_data)


# def get_preview(prompt_data: PromptData, preview_id: str, *args, **kwargs):
#     return prompt_data.get_preview_output(preview_id, *args, **kwargs)


# FUNCTIONS = {
#     "update_prompt_data": update_prompt_data,
#     "get_prompt_data": get_prompt_data,
#     "preview_basic": preview_basic,
# }

# TODO: Make less cryptic (here '$' has two meanings which is extremely confusing)
# TODO: Implement kwargs
SERVER_CALL_COMMAND_TEMPLATE = Template(
    "args=$(jq --compact-output --null-input '$ARGS.positional' --args -- $placeholders)"
    ' && echo "{\\"server_call_name\\":\\"$server_call_name\\",\\"args\\":$args, \\"kwargs\\": {}}" | nc localhost $socket_number'
)


class Request(pydantic.BaseModel):
    server_call_name: str
    args: list = []
    kwargs: dict = {}


# TODO: Add support for index {n} and indices {+n}
# TODO: Will logging slow it down too much?
class ServerCall(ShellCommand):
    def __init__(self, function: Callable) -> None:
        self.function = function
        self.name = function.__name__
        signature = inspect.signature(function)
        parameters = list(signature.parameters.keys())[1:]  # excludes prompt_data
        placeholders = [PLACEHOLDERS[param] for param in parameters]
        super().__init__(
            SERVER_CALL_COMMAND_TEMPLATE.safe_substitute(
                {"server_call_name": self.name, "placeholders": " ".join(placeholders)}
            )
        )

    def resolve(self, socket_number: int) -> None:
        self.safe_substitute({"socket_number": socket_number})


class Server(Thread):
    def __init__(self, prompt_data: PromptData, server_setup_finished: Event, *, daemon: bool | None = None) -> None:
        super().__init__(daemon=daemon)
        self.prompt_data = prompt_data
        self.server_setup_finished = server_setup_finished
        self.server_calls: dict[str, ServerCall] = {
            action.name: action for action in prompt_data.action_menu.actions if isinstance(action, ServerCall)
        } | {
            preview.command.name: preview.command
            for preview in prompt_data.previewer.previews.values()
            if isinstance(preview.command, ServerCall)
        }

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("localhost", 0))
            socket_specs = server_socket.getsockname()
            socket_number = socket_specs[1]
            for action in self.prompt_data.action_menu.actions:
                logger.debug(action)
                if isinstance(action, ServerCall):
                    action.resolve(socket_number)
                    logger.debug(action)
            for preview in self.prompt_data.previewer.previews.values():
                logger.debug(preview.command)
                if isinstance(preview.command, ServerCall):
                    preview.command.resolve(socket_number)
                    logger.debug(preview.command)
            server_socket.listen()
            logger.info(f"Server listening on {socket_specs}...")

            self.server_setup_finished.set()
            while True:
                client_socket, addr = server_socket.accept()
                logger.info(f"Connection from {addr}")
                self.handle_request(client_socket, self.prompt_data)

    def handle_request(self, client_socket: socket.socket, prompt_data: PromptData):
        # print(client_socket)
        if r := client_socket.recv(1024):
            payload = r.decode("utf-8").strip()
            logger.debug(payload)
            try:
                request = pydantic.parse_raw_as(Request, payload)
                response = self.server_calls[request.server_call_name].function(
                    prompt_data, *request.args, **request.kwargs
                )
            except Exception:
                response = traceback.format_exc()
                # print(response)
            if response:
                client_socket.sendall(response.encode("utf-8"))
        client_socket.close()


if __name__ == "__main__":
    ...
