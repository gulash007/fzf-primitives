from __future__ import annotations

import json
import socket
import traceback
from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..action_menu import Binding
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..options import EndStatus
from .actions import (
    PostProcessor,
    PromptEndingAction,
    Request,
    ServerCall,
    ServerCallFunction,
    ServerCallFunctionGeneric,
)
from .request import MAKE_SERVER_CALL_ENV_VAR_NAME, SOCKET_NUMBER_ENV_VAR, CommandOutput, PromptState

__all__ = [
    "Server",
    "ServerCall",
    "ServerCallFunction",
    "ServerCallFunctionGeneric",
    "PostProcessor",
    "PromptEndingAction",
    "PromptState",
    "CommandOutput",
    "EndStatus",
    "MAKE_SERVER_CALL_ENV_VAR_NAME",
    "SOCKET_NUMBER_ENV_VAR",
]


class Server[T, S](Thread, LoggedComponent):
    def __init__(self, prompt_data: PromptData[T, S]) -> None:
        LoggedComponent.__init__(self)
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.setup_finished = Event()
        self.should_close = Event()
        self.server_calls: dict[str, ServerCall[T, S]] = {}
        self.socket_number: int

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            # TODO: Use socket.AF_UNIX
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("localhost", 0))
                socket_specs = server_socket.getsockname()
                self.socket_number = socket_specs[1]
                server_socket.listen()
                self.logger.info(f"Server listening on {socket_specs}...")

                self.setup_finished.set()
                server_socket.settimeout(0.05)
                while True:
                    try:
                        client_socket, addr = server_socket.accept()
                    except TimeoutError:
                        if self.should_close.is_set():
                            self.logger.info("Server closing")
                            break
                        continue
                    self._handle_request(client_socket, self.prompt_data)
        except Exception as e:
            self.logger.exception(e)
            raise
        finally:
            self.setup_finished.set()

    def _handle_request(self, client_socket: socket.socket, prompt_data: PromptData[T, S]):
        payload_length = int.from_bytes(client_socket.recv(4))
        payload = client_socket.recv(payload_length, socket.MSG_WAITALL).decode("utf-8")
        self.logger.debug(f"Received payload: {payload}")
        response = ""
        try:
            request = Request.from_json(json.loads(payload))
            self.logger.debug(
                f"Resolving '{request.server_call_id}' ({len(self.server_calls)} server calls registered)"
            )
            response = self.server_calls[request.server_call_id].run(prompt_data, request) or response
        except Exception as err:
            self.logger.error(trb := traceback.format_exc())
            payload_info = f"Payload contents:\n{payload}"
            self.logger.error(payload_info)
            response = f"{trb}\n{payload_info}"
            if isinstance(err, KeyError):
                response = f"{trb}\n{list(self.server_calls.keys())}"
                self.logger.error(f"Available server calls:\n{list(self.server_calls.keys())}")
        finally:
            response_bytes = str(response).encode("utf-8")
            client_socket.send(len(response_bytes).to_bytes(4))
            client_socket.sendall(response_bytes)
            client_socket.close()

    def add_server_calls(self, binding: Binding):
        for action in binding.actions:
            if isinstance(action, ServerCall):
                self.add_server_call(action)

    def add_server_call(self, server_call: ServerCall):
        if server_call.id not in self.server_calls:
            self.logger.debug(f"🤙 Adding server call: {server_call}")
            self.server_calls[server_call.id] = server_call
