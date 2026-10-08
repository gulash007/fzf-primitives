from __future__ import annotations

import socket
from threading import Event, Thread
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ..action_menu import Action
    from ..options import Trigger
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from .actions import SOCKET_NUMBER_ENV_VAR, ServerCall
from .ServerEndpoint import ServerEndpoint


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
        payload = payload_bytearray.decode("utf-8")
        try:
            endpoint_id, *fields = self._parse_payload(payload)
            endpoint = self._get_endpoint(endpoint_id)
        except Exception as err:
            self.logger.error(err)
            self._send_response(client_socket, str(err))
            client_socket.close()
        else:
            if endpoint.bg:
                Thread(target=self._run_endpoint, args=(client_socket, prompt_data, endpoint, fields)).start()
            else:
                self._run_endpoint(client_socket, prompt_data, endpoint, fields)

    def _run_endpoint(
        self, client_socket: socket.socket, prompt_data: PromptData[T, S], endpoint: ServerEndpoint, fields: list[str]
    ):
        try:
            response = endpoint.run(prompt_data, fields)
        except Exception as err:
            import traceback

            trb = traceback.format_exc()
            fields_info = f"Fields:\n\t{'\n\t'.join(fields)}"
            message = f"Error occurred while running endpoint '{endpoint.id}':\n{err}\n{trb}\n{fields_info}"
            self.logger.error(message)
            self._send_response(client_socket, message)
        else:
            if response:
                self._send_response(client_socket, str(response))
        finally:
            client_socket.close()

    def _parse_payload(self, payload: str) -> list[str]:
        try:
            return ServerCall.parse_payload(payload)
        except Exception as err:
            import traceback

            trb = traceback.format_exc()
            raise ServerFailedToParsePayload(f"Failed to parse payload:\n{trb}\nPayload contents:\n{payload}") from err

    def _get_endpoint(self, endpoint_id: str) -> ServerEndpoint:
        self.logger.debug(f"Resolving '{endpoint_id}' ({len(self.endpoints)} server calls registered)")
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            raise ServerEndpointNotFound(f"Server endpoint '{endpoint_id}' not found")
        return endpoint

    def _send_response(self, client_socket: socket.socket, response: str):
        try:
            client_socket.sendall(response.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError):
            pass

    def add_endpoints(self, actions: Iterable[Action], trigger: Trigger):
        for action in actions:
            if isinstance(action, ServerCall):
                self.add_endpoint(action, trigger)

    def add_endpoint(self, server_call: ServerCall[T, S], trigger: Trigger):
        if server_call.id in self.endpoints:
            raise ReusedServerCall(
                f"ServerCall ({server_call.name}) already resolved as endpoint. Please use unique ServerCall instances."
            )
        endpoint = ServerEndpoint(server_call.function, server_call.id, trigger, bg=server_call.bg)
        self.logger.debug(f"🤙 Adding server endpoint: {endpoint.id}", trace_point="adding_server_endpoint")
        self.endpoints[endpoint.id] = endpoint


class ReusedServerCall(Exception):
    pass


class ServerFailedToParsePayload(Exception):
    pass


class ServerEndpointNotFound(Exception):
    pass
