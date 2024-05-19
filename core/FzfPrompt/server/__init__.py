from __future__ import annotations

import json
import traceback
from multiprocessing.connection import Connection, Listener
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
from .request import MAKE_SERVER_CALL_ENV_VAR_NAME, SOCKET_NUMBER_ENV_VAR_NAME, CommandOutput, PromptState

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
    "SOCKET_NUMBER_ENV_VAR_NAME",
]


class Server[T, S](Thread, LoggedComponent):
    def __init__(self, prompt_data: PromptData[T, S]) -> None:
        LoggedComponent.__init__(self)
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.setup_finished = Event()
        self.server_calls: dict[str, ServerCall[T, S]] = {}
        self.socket_number: str
        self.listener: Listener

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            # TODO: Use socket.AF_UNIX
            address = ("localhost", 0)  # family is deduced to be 'AF_INET'
            with Listener(address, authkey=b"secret password") as listener:
                self.listener = listener
                socket_specs = listener.address
                self.socket_number = str(socket_specs[1])
                self.logger.info(f"Server listening on {socket_specs}...")

                self.setup_finished.set()
                while True:
                    try:
                        connection = listener.accept()
                    except ConnectionAbortedError:
                        self.logger.info("Server closing")
                        break
                    self._handle_request(connection, self.prompt_data)
        except Exception as e:
            self.logger.exception(e)
            raise
        finally:
            self.setup_finished.set()

    def _handle_request(self, connection: Connection, prompt_data: PromptData[T, S]):
        try:
            payload = connection.recv()
            request = Request.from_json(json.loads(payload))
            self.logger.debug(
                f"Resolving '{request.server_call_id}' ({len(self.server_calls)} server calls registered)"
            )
            response = self.server_calls[request.server_call_id].run(prompt_data, request)
        except Exception as err:
            self.logger.error(trb := traceback.format_exc())
            payload_info = f"Payload contents:\n{payload}"
            self.logger.error(payload_info)
            response = f"{trb}\n{payload_info}"
            if isinstance(err, KeyError):
                response = f"{trb}\n{list(self.server_calls.keys())}"
                self.logger.error(f"Available server calls:\n{list(self.server_calls.keys())}")
        finally:
            connection.send(str(response))
            connection.close()

    def add_server_calls(self, binding: Binding):
        for action in binding.actions:
            if isinstance(action, ServerCall):
                self.add_server_call(action)

    def add_server_call(self, server_call: ServerCall):
        if server_call.id not in self.server_calls:
            self.logger.debug(f"🤙 Adding server call: {server_call}")
            self.server_calls[server_call.id] = server_call
