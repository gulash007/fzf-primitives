from __future__ import annotations

from typing import Callable

from ...FzfPrompt import Binding, ConflictResolution, PromptData, ServerCall
from ...FzfPrompt.options.events import Hotkey, Situation
from ..event_adder import attach_hotkey_adder, attach_situation_adder
from ..on_event import OnEventBase
from .inspection import INSPECTION_ENDPOINT
from .inspector_prompt import get_inspector_prompt


class InspectorMod[T, S]:
    def __init__(self):
        self._mods: list[Callable[[PromptData], None]] = [lambda pd: pd.server.add_endpoint(INSPECTION_ENDPOINT)]

    def __call__(self, prompt_data: PromptData[T, S]):
        try:
            for mod in self._mods:
                mod(prompt_data)
        finally:
            self.clear()

    def clear(self):
        self._mods = []

    def attach_to_remote_inspector_prompt(self, backend_port: int, control_port: int):
        self.on_situation(on_conflict="append").START.pipe_backend_port_to_remote_inspector(backend_port)
        self.on_situation(on_conflict="append").FOCUS.refresh_remote_inspector_prompt(control_port)

    @attach_hotkey_adder
    def on_hotkey(self, *hotkeys: Hotkey, on_conflict: ConflictResolution = "raise error") -> InspectorOnEvent[T, S]:
        return self.on_event(*hotkeys, on_conflict=on_conflict)

    @attach_situation_adder
    def on_situation(
        self, *situations: Situation, on_conflict: ConflictResolution = "raise error"
    ) -> InspectorOnEvent[T, S]:
        return self.on_event(*situations, on_conflict=on_conflict)

    def on_event(self, *events: Hotkey | Situation, on_conflict: ConflictResolution = "raise error"):
        on_event_mod = InspectorOnEvent[T, S](*events, on_conflict=on_conflict)
        self._mods.append(on_event_mod)
        return on_event_mod


class InspectorOnEvent[T, S](OnEventBase):
    @property
    def run_inspector_prompt(self):
        self._binding += Binding("Run inspector prompt", ServerCall(lambda pd: get_inspector_prompt(pd).run()))
        return self

    def pipe_backend_port_to_remote_inspector(self, backend_port: int):
        self._binding += Binding(
            "Pipe backend port to remote inspector",
            ServerCall(
                lambda pd: pd.logger.debug(
                    pd.make_server_call(backend_port, "CHANGE_INSPECTED_PORT", None, _port=str(pd.server.port))
                )
            ),
        )
        return self

    def refresh_remote_inspector_prompt(self, control_port: int):
        self._binding += Binding(
            "Refresh remote inspector",
            ServerCall(
                lambda pd: pd.controller.execute(control_port, Binding(None, "refresh-preview")),
                command_type="execute-silent",
            ),
        )
        return self
