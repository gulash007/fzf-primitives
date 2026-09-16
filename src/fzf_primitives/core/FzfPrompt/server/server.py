from __future__ import annotations

import socket
from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..action_menu import Binding
    from ..options import Trigger
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from .actions import SOCKET_NUMBER_ENV_VAR, ServerCall
from .request import ServerEndpoint


class Server[T, S](Thread, LoggedComponent):
    def __init__(self, prompt_data: PromptData[T, S]) -> None:
        LoggedComponent.__init__(self)
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.setup_finished = Event()
        self.should_close = Event()
        self.endpoints: dict[str, ServerEndpoint] = {}
        self.port: int

    def set_port(self, port: int) -> None:
        self.port = port

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            # TODO: Use socket.AF_UNIX
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("localhost", 0))
                socket_specs = server_socket.getsockname()
                self.set_port(socket_specs[1])
                self.prompt_data.fzf_env[SOCKET_NUMBER_ENV_VAR] = str(self.port)

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
        payload_bytearray = bytearray()
        while r := client_socket.recv(1024):
            payload_bytearray.extend(r)
        payload = payload_bytearray.decode("utf-8").strip()
        try:
            endpoint_id, *fields = ServerCall.parse_payload(payload)
            self.logger.debug(f"Resolving '{endpoint_id}' ({len(self.endpoints)} server calls registered)")
            response = self.endpoints[endpoint_id].run(prompt_data, fields)
        except Exception as err:
            import traceback

            self.logger.error(trb := traceback.format_exc())
            payload_info = f"Payload contents:\n{payload}"
            self.logger.error(payload_info)
            response = f"{trb}\n{payload_info}"
            if isinstance(err, KeyError):
                response = f"{trb}\n{list(self.endpoints.keys())}"
                self.logger.error(f"Available server calls:\n{list(self.endpoints.keys())}")
            client_socket.sendall(str(response).encode("utf-8"))
        else:
            if response:
                client_socket.sendall(str(response).encode("utf-8"))
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
