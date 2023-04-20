# Black magic layer
import socket
import traceback
from threading import Event
from typing import Callable, Literal

import pydantic

from .PromptData import Preview, PreviewName, PromptData


def update_prompt_data(prompt_data: PromptData, query: str, *selections: str):
    prompt_data.update(query, selections)
    # print("Updated to:", prompt_data)
    return f"Updated prompt data: {prompt_data}"


def get_prompt_data(prompt_data: PromptData):
    return str(prompt_data)


def get_preview(prompt_data: PromptData, preview_id: PreviewName):
    return prompt_data.get_preview_output(preview_id)


FunctionName = Literal["update_prompt_data", "get_prompt_data", "get_preview"]

FUNCTIONS: dict[FunctionName, Callable] = {
    "update_prompt_data": update_prompt_data,
    "get_prompt_data": get_prompt_data,
    "get_preview": get_preview,
}


class Request(pydantic.BaseModel):
    function_name: FunctionName
    args: list = []
    kwargs: dict = {}


def handle_request(client_socket: socket.socket, prompt_data: PromptData):
    # print(client_socket)
    if r := client_socket.recv(1024):
        # print(r)
        payload = r.decode("utf-8")
        try:
            request = pydantic.parse_raw_as(Request, payload.strip())
            response = FUNCTIONS[request.function_name](prompt_data, *request.args, **request.kwargs)
        except Exception:
            response = traceback.format_exc()
            # print(response)
        if response:
            client_socket.sendall(response.encode("utf-8"))
    client_socket.close()


REQUEST_COMMAND = (
    "args=$(jq --compact-output --null-input '$ARGS.positional' --args -- {q} {+})"
    ' && echo "{\\"function_name\\":\\"%s\\",\\"args\\":$args}" | nc localhost %i'
)


class RequestCall:
    def __init__(self, function_name: FunctionName | None, socket_number: int | None) -> None:
        self.function_name = function_name
        self.socket_number = socket_number

    def __str__(self) -> str:
        if self.function_name is None or self.socket_number is None:
            raise ValueError(f"RequestCall not completely formatted: {self.__dict__}")
        return REQUEST_COMMAND % (self.function_name, self.socket_number)


# TODO: Will logging slow it down too much?
def start_server(prompt_data: PromptData, prompt_data_finished_contextualizing: Event | None = None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("localhost", 0))
        socket_specs = server_socket.getsockname()
        socket_number = socket_specs[1]
        print(socket_number)
        update_call = RequestCall("update_prompt_data", socket_number)
        update_action = f"execute-silent({update_call})"
        # print(update_action)
        prompt_data.options.on_event("change", update_action)
        prompt_data.options.on_event("focus", update_action)
        prompt_data.resolve_previews(socket_number)
        if prompt_data_finished_contextualizing is not None:
            prompt_data_finished_contextualizing.set()
        # print(prompt_data.options)
        server_socket.listen()
        # print(f"Server listening on {socket_specs}...")

        while True:
            client_socket, addr = server_socket.accept()
            # print(f"Connection from {addr}")
            handle_request(client_socket, prompt_data)


if __name__ == "__main__":
    start_server(PromptData(previews={"basic": Preview(id="basic")}))
