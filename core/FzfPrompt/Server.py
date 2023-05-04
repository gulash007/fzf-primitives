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

from ..actions.functions import preview_basic
from .ActionMenu import Action
from .commands.fzf_placeholders import PLACEHOLDERS
from .options import Hotkey

if TYPE_CHECKING:
    from ..mods import Moddable, P
    from .Previewer import Preview
    from .PromptData import PromptData


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


REQUEST_COMMAND = (
    "args=$(jq --compact-output --null-input '$ARGS.positional' --args -- $placeholders)"
    ' && echo "{\\"server_call_name\\":\\"$server_call_name\\",\\"args\\":$args}" | nc localhost $socket_number'
)


class Request(pydantic.BaseModel):
    server_call_name: str
    args: list = []
    kwargs: dict = {}


@dataclass
class ServerCall:
    name: str
    function: Callable
    hotkey: Hotkey

    # TODO: generate properly set-up Action
    def __post_init__(self):
        self.unformatted_command = self.get_template_from_function()

    def action(self, socket_number: int) -> Action:  # TODO: resolve last
        command = self.unformatted_command.safe_substitute({"socket_number": socket_number})
        return Action(self.name, f"execute-silent({command})", self.hotkey)

    def __call__(self, func: Moddable[P]) -> Moddable[P]:
        def with_server_call(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.add_server_call(self)
            return func(prompt_data, *args, **kwargs)

        return with_server_call

    def get_template_from_function(self) -> Template:
        signature = inspect.signature(self.function)
        parameters = list(signature.parameters.keys())[1:]  # excludes prompt_data
        placeholders = [PLACEHOLDERS[param] for param in parameters]
        return Template(
            Template(REQUEST_COMMAND).safe_substitute(
                {"server_call_name": self.name, "placeholders": " ".join(placeholders)}
            )
        )


# TODO: Add support for index {n} and indices {+n}
# TODO: Will logging slow it down too much?


class Server(Thread):
    def __init__(self, prompt_data: PromptData, server_setup_finished: Event, *, daemon: bool | None = None) -> None:
        super().__init__(daemon=daemon)
        self.prompt_data = prompt_data
        self.server_setup_finished = server_setup_finished

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("localhost", 0))
            socket_specs = server_socket.getsockname()
            socket_number = socket_specs[1]
            self.prompt_data.resolve_server_calls(socket_number)
            server_socket.listen()
            # print(f"Server listening on {socket_specs}...")

            if self.server_setup_finished is not None:
                self.server_setup_finished.set()
            while True:
                client_socket, addr = server_socket.accept()
                # print(f"Connection from {addr}")
                self.handle_request(client_socket, self.prompt_data)

    def handle_request(self, client_socket: socket.socket, prompt_data: PromptData):
        # print(client_socket)
        if r := client_socket.recv(1024):
            # print(r)
            payload = r.decode("utf-8")
            try:
                request = pydantic.parse_raw_as(Request, payload.strip())
                response = prompt_data.server_calls[request.server_call_name].function(
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
