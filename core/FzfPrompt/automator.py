from __future__ import annotations

import time
from threading import Event, Thread
from typing import TYPE_CHECKING

import clipboard
import requests

if TYPE_CHECKING:
    from .prompt_data import PromptData
    from .action_menu import ActionMenu
from . import action_menu as am
from .server import ServerCall
from ..monitoring import Logger

logger = Logger.get_logger()


class Automator(Thread):
    @property
    def port(self) -> str:
        if self.__port is None:
            raise RuntimeError("port not set")
        return self.__port

    @port.setter
    def port(self, value: str):
        self.__port = value
        logger.info(f"Automator listening on port {self.port}")

    def __init__(self) -> None:
        self.__port: str | None = None
        self.bindings: list[am.Binding] = []
        self.port_resolved = Event()
        self.binding_executed = Event()
        self.move_to_next_binding_server_call = ServerCall(self.move_to_next_binding)
        super().__init__()

    def run(self):
        try:
            while not self.port_resolved.is_set():
                if not self.port_resolved.wait(timeout=5):
                    logger.warning("Waiting for port to be resolved…")
            for binding_to_automate in self.bindings:
                self.execute_binding(binding_to_automate)
        except Exception as e:
            logger.exception(e)
            raise

    def add_bindings(self, *bindings: am.Binding):
        self.bindings.extend(bindings)

    def execute_binding(self, binding: am.Binding):
        logger.debug(f"Automating {binding}")
        if not binding.final_action:
            binding += am.Binding("move to next automated binding", self.move_to_next_binding_server_call)
        self.binding_executed.clear()
        response = requests.post(f"http://localhost:{self.port}", data=binding.to_action_string())
        if message := response.text:
            if not message.startswith("unknown action:"):
                logger.weirdness(message)  # type: ignore
            raise RuntimeError(message)
        if binding.final_action:
            return
        self.binding_executed.wait()
        time.sleep(0.25)

    def move_to_next_binding(self, prompt_data: PromptData):
        self.binding_executed.set()

    def resolve(self, action_menu: ActionMenu):
        action_menu.add(
            "start", am.Binding("get automator port", ServerCall(self.get_port_number)), conflict_resolution="prepend"
        )
        self.add_bindings(
            *[x if isinstance(x, am.Binding) else action_menu.bindings[x] for x in action_menu.to_automate]
        )

    def get_port_number(self, prompt_data: PromptData, FZF_PORT: str):
        """Utilizes the $FZF_PORT variable containing the port assigned to --listen option
        (or the one generated automatically when --listen=0)"""
        self.port = FZF_PORT
        clipboard.copy(FZF_PORT)
        self.port_resolved.set()
