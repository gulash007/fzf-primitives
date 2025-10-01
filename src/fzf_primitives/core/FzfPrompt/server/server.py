from __future__ import annotations

import json
import socket
import traceback
from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..action_menu import Binding
    from ..options import Trigger
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from . import make_server_call
from .actions import (
    MAKE_SERVER_CALL_ENV_VAR_NAME,
    SOCKET_NUMBER_ENV_VAR,
    ServerCall,
)
from .request import Request, ServerEndpoint


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
                self.prompt_data.fzf_env[SOCKET_NUMBER_ENV_VAR] = str(self.port)
                self.prompt_data.fzf_env[MAKE_SERVER_CALL_ENV_VAR_NAME] = make_server_call.__file__

                server_socket.listen()
                self.logger.info(f"Server listening on {socket_specs}...", trace_point="server_listening")

                self.setup_finished.set()
                server_socket.settimeout(0.05)
                while True:
                    try:
                        client_socket, addr = server_socket.accept()
                    except TimeoutError:
                        if self.should_close.is_set():
                            self.logger.info("Server closing", trace_point="server_closing")
                            break
                        continue
                    self._handle_request(client_socket, self.prompt_data)
        except Exception as e:
            self.logger.exception(str(e), trace_point="error_in_server")
            raise
        finally:
            self.setup_finished.set()

    def _handle_request(self, client_socket: socket.socket, prompt_data: PromptData[T, S]):
        payload_length = int.from_bytes(client_socket.recv(4))
        payload = client_socket.recv(payload_length, socket.MSG_WAITALL).decode("utf-8")

        response = ""
        try:
            request = Request.from_json(json.loads(payload))
            endpoint = self.endpoints[request.endpoint_id]
            self.logger.debug(
                f"Resolving {endpoint.trigger}:'{request.endpoint_id}' ({len(self.endpoints)} endpoints registered)",
                trace_point="resolving_server_call",
                trigger=endpoint.trigger,
            )
            response = endpoint.run(prompt_data, request) or response
        except Exception as err:
            trb = traceback.format_exc()
            error_message = f"{trb}\nPayload contents:\n{payload}"
            self.logger.error("{}", error_message, trace_point="error_handling_request")
            response = error_message
            if isinstance(err, KeyError):
                response = f"{trb}\n{list(self.endpoints.keys())}"
                self.logger.error(
                    f"Available server calls:\n{list(self.endpoints.keys())}", trace_point="missing_server_call"
                )
        finally:
            response_bytes = str(response).encode("utf-8")
            try:
                client_socket.send(len(response_bytes).to_bytes(4))
                client_socket.sendall(response_bytes)
            except Exception as e:
                self.logger.exception(f"Error sending response: {e}", trace_point="error_sending_response")
            finally:
                client_socket.close()

    def add_endpoints(self, binding: Binding[T, S], trigger: Trigger):
        for action in binding.actions:
            if isinstance(action, ServerCall):
                self.add_endpoint(action, trigger)

    def add_endpoint(self, action: ServerCall[T, S], trigger: Trigger):
        if action.id in self.endpoints:
            raise ReusedServerCall(
                f"ServerCall ({action.name}) already resolved as endpoint. Please use unique ServerCall instances."
            )
        endpoint = ServerEndpoint(action.function, action.id, trigger)
        self.logger.debug(f"🤙 Adding server endpoint: {endpoint.id}", trace_point="adding_server_endpoint")
        self.endpoints[endpoint.id] = endpoint


class ReusedServerCall(Exception):
    pass
