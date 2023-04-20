# Black magic layer
import json
import socket

import pydantic


if __name__ == "__main__":
    __package__ = "fzf_primitives.experimental.core.intercom"

from .previews import PREVIEW
from .PromptData import Preview, PromptData


def update_prompt_data(prompt_data: PromptData, query: str, selections: list[str]):
    prompt_data.update(query, selections)
    print("Updated to:", prompt_data)
    return f"Updated prompt data: {prompt_data}"


def get_prompt_data(prompt_data: PromptData):
    return str(prompt_data)


def get_preview(prompt_data: PromptData, preview_id: str):
    return prompt_data.get_preview_output(preview_id)


FUNCTIONS = {"update_prompt_data": update_prompt_data, "get_prompt_data": get_prompt_data, "get_preview": get_preview}


class Request(pydantic.BaseModel):
    function_name: str
    args: list = []
    kwargs: dict = {}


def handle_request(client_socket: socket.socket, prompt_data: PromptData):
    print(client_socket)
    if r := client_socket.recv(1024):
        payload = r.decode("utf-8")
        try:
            request = pydantic.parse_raw_as(Request, payload)
            response = FUNCTIONS[request.function_name](prompt_data, *request.args, **request.kwargs)
        except Exception as e:
            response = f"{type(e)}: {e}"
        if response:
            client_socket.sendall(response.encode("utf-8"))
    client_socket.close()

# TODO: Start in a thread
def start_server(prompt_data: PromptData):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("localhost", 0))
        server_socket.listen()
        print(f"Server listening on {server_socket.getsockname()}...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_request(client_socket, prompt_data)


if __name__ == "__main__":
    start_server(PromptData(previews={"basic": Preview(id="basic", command="")}))
