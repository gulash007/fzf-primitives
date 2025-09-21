from __future__ import annotations

import time
from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .options import Hotkey
    from .prompt_data import PromptData
from ...config import Config
from ..monitoring import LoggedComponent
from .action_menu import Action, Binding, Transform
from .controller import Controller
from .decorators import single_use_method
from .server import ServerCall


class Automator[T, S](Thread, LoggedComponent):
    def __init__(self, prompt_data: PromptData[T, S]) -> None:
        LoggedComponent.__init__(self)
        self._prompt_data = prompt_data
        self._controller = Controller()
        self.__port: int | None = None
        self._bindings: list[Binding] = []
        self._binding_executed = Event()
        self.automator_transform = Transform(self._actions_builder)
        self._current_actions_to_automate: list[Action[T, S]]
        super().__init__(daemon=True)

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
            self.logger.exception(str(e), trace_point="error_in_automator")

    @single_use_method
    def prepare(self):
        # HACK: Injected trigger (endpoint wasn't actually triggered by 'start' event)
        self._prompt_data.server.add_endpoint(self.automator_transform, "start")
        self._prompt_data.options.listen()

    def execute_binding(self, binding: Binding):
        time.sleep(Config.automator_delay)
        self.logger.debug(f">>>>> Automating {binding}", trace_point="automating_binding", binding=binding.name)
        if not binding.final_action:
            binding += Binding(
                "move to next automated binding", ServerCall(self._move_to_next_binding, command_type="execute-silent")
            )
        self._current_actions_to_automate = binding.actions
        self._binding_executed.clear()
        self._controller.execute(self.port, Binding("automated binding", self.automator_transform))
        if binding.final_action:
            return
        self._binding_executed.wait()

    def _actions_builder(self, prompt_data: PromptData) -> list[Action[T, S]]:
        return self._current_actions_to_automate

    def _move_to_next_binding(self, prompt_data: PromptData):
        self._binding_executed.set()

    def _resolve_port(self):
        sleep_period = 0.01
        total_sleep_time = 0
        log_every_n_seconds = 5
        while True:
            try:
                self.__port = self._prompt_data.control_port
                break
            except RuntimeError:
                if total_sleep_time >= log_every_n_seconds:
                    self.logger.warning("Waiting for port to be resolved…")
                    total_sleep_time = 0
                time.sleep(sleep_period)
                total_sleep_time += sleep_period

    # TODO: Also allow automating default fzf hotkeys (can be solved by creating appropriate bindings in the action menu)
    def automate(self, *to_automate: Hotkey):
        self._bindings.extend(self._prompt_data.action_menu.bindings[hotkey] for hotkey in to_automate)

    def automate_actions(self, *actions: Action[T, S], name: str | None = None):
        self._bindings.append(Binding(name or "anonymous actions", *actions))
