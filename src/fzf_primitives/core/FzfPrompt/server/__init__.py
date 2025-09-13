from __future__ import annotations

import json
import socket
import tempfile
import traceback
from pathlib import Path
from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..action_menu import Binding
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..options import EndStatus
from . import make_server_call
from .actions import (
    MAKE_SERVER_CALL_ENV_VAR_NAME,
    SOCKET_NUMBER_ENV_VAR,
    SOCKET_PATH_ENV_VAR,
    CommandOutput,
    PostProcessor,
    PromptEndingAction,
    ServerCall,
    ServerCallFunction,
    ServerCallFunctionGeneric,
)
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
        self.socket_path: Path

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            socket_dir = Path(tempfile.gettempdir()) / "app_sockets"
            socket_dir.mkdir(exist_ok=True)
            socket_path = socket_dir / f"server_{id(self)}.sock"

            # Clean up any existing socket file
            try:
                socket_path.unlink()
            except FileNotFoundError:
                pass

            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(str(socket_path))

                self.socket_path = socket_path  # TODO: Use it?
                self.prompt_data.run_vars["env"][SOCKET_PATH_ENV_VAR] = str(socket_path)
                self.prompt_data.run_vars["env"][MAKE_SERVER_CALL_ENV_VAR_NAME] = make_server_call.__file__

                server_socket.listen()
                self.logger.info(f"Server listening on Unix socket: {socket_path}")
                self.setup_finished.set()
                server_socket.settimeout(0.05)
                try:
                    while True:
                        try:
                            client_socket, addr = server_socket.accept()
                        except socket.timeout:
                            if self.should_close.is_set():
                                self.logger.info("Server closing")
                                return
                            continue
                        self._handle_request(client_socket, self.prompt_data)
                finally:
                    # Clean up socket file when done
                    try:
                        socket_path.unlink()
                    except FileNotFoundError:
                        pass
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
            self.logger.debug(
                f"Resolving '{request.endpoint_id}' ({len(self.endpoints)} endpoints registered)",
                trace_point="resolving_server_call",
            )
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
            try:
                client_socket.send(len(response_bytes).to_bytes(4))
                client_socket.sendall(response_bytes)
            except Exception as e:
                self.logger.exception(f"Error sending response: {e}")
            finally:
                client_socket.close()

    def add_endpoints(self, binding: Binding):
        for action in binding.actions:
            if isinstance(action, ServerCall):
                self.add_endpoint(action.endpoint)

    def add_endpoint(self, endpoint: ServerEndpoint):
        if endpoint.id not in self.endpoints:
            self.logger.debug(f"🤙 Adding server endpoint: {endpoint.id}", trace_point="adding_server_endpoint")
            self.endpoints[endpoint.id] = endpoint
