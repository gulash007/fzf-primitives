from __future__ import annotations

import time
from threading import Event, Thread
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .prompt_data import PromptData
from ..monitoring import Logger
from . import action_menu as am
from .decorators import single_use_method
from .server import ServerCall

logger = Logger.get_logger()


class Automator(Thread):

    def __init__(self) -> None:
        self.__port: str | None = None
        self._bindings: list[am.Binding] = []
        self._port_resolved = Event()
        self._binding_executed = Event()
        self.move_to_next_binding_server_call = ServerCall(self._move_to_next_binding)
        super().__init__()

    @property
    def port(self) -> str:
        if self.__port is None:
            raise RuntimeError("port not set")
        return self.__port

    @port.setter
    def port(self, value: str):
        self.__port = value

    def run(self):
        try:
            while not self._port_resolved.is_set():
                if not self._port_resolved.wait(timeout=5):
                    logger.warning("Waiting for port to be resolved…")
            for binding_to_automate in self._bindings:
                self.execute_binding(binding_to_automate)
        except Exception as e:
            logger.exception(e)
            raise

    @single_use_method
    def prepare(self, prompt_data: PromptData):
        self._bindings.extend(prompt_data.bindings_to_automate)
        prompt_data.action_menu.add(
            "start",
            am.Binding("get prompt port number for automator", ServerCall(self._get_port_number)),
            conflict_resolution="prepend",
        )
        prompt_data.action_menu.server_calls.append(self.move_to_next_binding_server_call)
        prompt_data.options.listen()

    def execute_binding(self, binding: am.Binding):
        time.sleep(0.25)
        logger.debug(f">>>>> Automating {binding}")
        if not binding.final_action:
            binding += am.Binding("move to next automated binding", self.move_to_next_binding_server_call)
        self._binding_executed.clear()
        response = requests.post(f"http://localhost:{self.port}", data=binding.to_action_string())
        if message := response.text:
            if not message.startswith("unknown action:"):
                logger.weirdness(message)  # type: ignore
            raise RuntimeError(message)
        if binding.final_action:
            return
        self._binding_executed.wait()

    def _move_to_next_binding(self, prompt_data: PromptData):
        self._binding_executed.set()

    def _get_port_number(self, prompt_data: PromptData, FZF_PORT: str):
        """Utilizes the $FZF_PORT variable containing the port assigned to --listen option
        (or the one generated automatically when --listen=0)"""
        self.port = FZF_PORT
        logger.debug(f"Automated prompt listens on {self.port}")
        self._port_resolved.set()
