from __future__ import annotations

import time
from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .options import Hotkey
    from .prompt_data import PromptData
from ..monitoring import LoggedComponent
from . import action_menu as am
from .action_menu import Action, Binding
from .controller import Controller
from .decorators import single_use_method
from .server import ServerCall


class Automator(Thread, LoggedComponent):
    def __init__(self, prompt_data: PromptData) -> None:
        LoggedComponent.__init__(self)
        self._prompt_data = prompt_data
        self._controller = Controller()
        self.__port: int | None = None
        self._bindings: list[am.Binding] = []
        self._binding_executed = Event()
        self.move_to_next_binding_server_call = ServerCall(self._move_to_next_binding)
        super().__init__()

    @property
    def port(self) -> int:
        if self.__port is None:
            raise RuntimeError("port not set")
        return self.__port

    def run(self):
        try:
            self._resolve_port()
            for binding_to_automate in self._bindings:
                self.execute_binding(binding_to_automate)
        except Exception as e:
            self.logger.exception(e)
            raise

    @single_use_method
    def prepare(self):
        self._bindings.extend(self._prompt_data.bindings_to_automate)
        self._prompt_data.server.add_endpoint(self.move_to_next_binding_server_call.endpoint)
        self._prompt_data.options.listen()

    def execute_binding(self, binding: am.Binding):
        time.sleep(0.25)  # TODO: add to config
        self.logger.debug(f">>>>> Automating {binding}")
        if not binding.final_action:
            binding += am.Binding("move to next automated binding", self.move_to_next_binding_server_call)
        self._binding_executed.clear()
        self._controller.execute(self.port, binding)
        if binding.final_action:
            return
        self._binding_executed.wait()

    def _move_to_next_binding(self, prompt_data: PromptData):
        self._binding_executed.set()

    def _resolve_port(self):
        sleep_period = 0.01
        total_sleep_time = 0
        log_every_n_seconds = 5
        while not self._prompt_data.control_port:
            if total_sleep_time >= log_every_n_seconds:
                self.logger.warning("Waiting for port to be resolved…")
                total_sleep_time = 0
            time.sleep(sleep_period)
            total_sleep_time += sleep_period
        self.__port = self._prompt_data.control_port

    # TODO: Also allow automating default fzf hotkeys (can be solved by creating appropriate bindings in the action menu)
    def automate(self, *to_automate: Hotkey):
        self._bindings.extend(self._prompt_data.action_menu.bindings[hotkey] for hotkey in to_automate)

    def automate_actions(self, *actions: Action, name: str | None = None):
        self._bindings.append(Binding(name or "anonymous actions", *actions))
