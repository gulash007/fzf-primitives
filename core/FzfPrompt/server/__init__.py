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
    MAKE_SERVER_CALL_ENV_VAR_NAME,
    SOCKET_NUMBER_ENV_VAR,
    CommandOutput,
    PostProcessor,
    PromptEndingAction,
    ServerCall,
    ServerCallFunction,
    ServerCallFunctionGeneric,
)
from . import make_server_call
from .request import PromptState, Request, ServerEndpoint

__all__ = [
    "Server",
    "ServerEndpoint",
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
        self.endpoints: dict[str, ServerEndpoint] = {}
        self.port: int

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            # TODO: Use socket.AF_UNIX
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("localhost", 0))
                socket_specs = server_socket.getsockname()
                self.port = socket_specs[1]
                self.prompt_data.run_vars["env"][SOCKET_NUMBER_ENV_VAR] = str(self.port)
                self.prompt_data.run_vars["env"][MAKE_SERVER_CALL_ENV_VAR_NAME] = make_server_call.__file__

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
        response = ""
        try:
            request = Request.from_json(json.loads(payload))
            self.logger.debug(f"Resolving '{request.endpoint_id}' ({len(self.endpoints)} endpoints registered)")
            response = self.endpoints[request.endpoint_id].run(prompt_data, request) or response
        except Exception as err:
            self.logger.error(trb := traceback.format_exc())
            payload_info = f"Payload contents:\n{payload}"
            self.logger.error(payload_info)
            response = f"{trb}\n{payload_info}"
            if isinstance(err, KeyError):
                response = f"{trb}\n{list(self.endpoints.keys())}"
                self.logger.error(f"Available server calls:\n{list(self.endpoints.keys())}")
        finally:
            response_bytes = str(response).encode("utf-8")
            client_socket.send(len(response_bytes).to_bytes(4))
            client_socket.sendall(response_bytes)
            client_socket.close()

    def add_endpoints(self, binding: Binding):
        for action in binding.actions:
            if isinstance(action, ServerCall):
                self.add_endpoint(action.endpoint)

    def add_endpoint(self, endpoint: ServerEndpoint):
        if endpoint.id not in self.endpoints:
            self.logger.debug(f"🤙 Adding server endpoint: {endpoint}")
            self.endpoints[endpoint.id] = endpoint
