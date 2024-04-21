from __future__ import annotations

import time
from threading import Event, Thread
from typing import TYPE_CHECKING

import clipboard
import requests

if TYPE_CHECKING:
    from .action_menu import ActionMenu
    from .prompt_data import PromptData
from ..monitoring import Logger
from . import action_menu as am
from .decorators import single_use_method
from .options import Hotkey, Options
from .server import ServerCall

logger = Logger.get_logger()


class Automator(Thread):

    def __init__(self, action_menu: ActionMenu) -> None:
        self.__port: str | None = None
        self.action_menu = action_menu
        self.bindings: list[am.Binding] = []
        self.port_resolved = Event()
        self.binding_executed = Event()
        self.move_to_next_binding_server_call = ServerCall(self.move_to_next_binding)
        super().__init__()

    @property
    def port(self) -> str:
        if self.__port is None:
            raise RuntimeError("port not set")
        return self.__port

    @port.setter
    def port(self, value: str):
        self.__port = value
        logger.info(f"Automated prompt listening on port {self.port}")

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

    @single_use_method
    def prepare(self):
        self.action_menu.add(
            "start",
            am.Binding("get prompt port number for automator", ServerCall(self.get_port_number)),
            conflict_resolution="prepend",
        )
        self.action_menu.server_calls.append(self.move_to_next_binding_server_call)

    # TODO: Also allow automating default fzf hotkeys (can be solved by creating appropriate bindings in the action menu)
    def automate(self, *to_automate: Hotkey):
        self.bindings.extend(self.action_menu.bindings[hotkey] for hotkey in to_automate)

    def automate_actions(self, *actions: am.Action, name: str | None = None):
        self.bindings.append(am.Binding(name or "anonymous actions", *actions))

    @property
    def should_run(self) -> bool:
        return bool(self.bindings)

    def execute_binding(self, binding: am.Binding):
        logger.debug(f">>>>> Automating {binding}")
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

    def get_port_number(self, prompt_data: PromptData, FZF_PORT: str):
        """Utilizes the $FZF_PORT variable containing the port assigned to --listen option
        (or the one generated automatically when --listen=0)"""
        self.port = FZF_PORT
        clipboard.copy(FZF_PORT)
        self.port_resolved.set()

    @single_use_method
    def resolve_options(self) -> Options:
        return Options().listen() if self.should_run else Options()
