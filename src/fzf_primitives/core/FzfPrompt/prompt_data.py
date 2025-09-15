from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Literal

if TYPE_CHECKING:
    from .automator import Automator
from ..monitoring import LoggedComponent
from .action_menu import ActionMenu, Binding
from .controller import Controller
from .decorators import single_use_method
from .options import Hotkey, Options, Event
from .previewer import Previewer
from .server import EndStatus, PostProcessor, PromptState, Server, ServerCall
from .server.make_server_call import make_server_call


class PromptData[T, S](LoggedComponent):
    """Accessed from fzf process through socket Server"""

    def __init__(
        self,
        entries: list[T] | None = None,
        converter: Callable[[T], str] = str,
        obj: S = None,
        previewer: Previewer[T, S] | None = None,
        action_menu: ActionMenu[T, S] | None = None,
        options: Options | None = None,
    ):
        super().__init__()
        self.logger.debug("PromptData created", trace_point="prompt_data_created")
        self.entries = entries or []
        self.converter = converter
        self.obj = obj
        self.action_menu = action_menu or ActionMenu()
        self.server = Server(self)
        self.previewer = previewer or Previewer()
        self._automator: Automator | None = None
        self._controller: Controller | None = None
        self.bindings_to_automate: list[Binding] = []
        self.options = options or Options()
        self.post_processors: list[PostProcessor] = []
        self._state: PromptState | None = None
        self._result: Result[T, S]
        self.id = datetime.now().isoformat()  # TODO: Use it?
        self.run_vars: dict[str, Any] = {"env": os.environ.copy()}
        self._stage: PromptStage = "created"
        self._control_port: int | None = None
        self.make_server_call = make_server_call

    @property
    def state(self) -> PromptState:
        if not self._state:
            raise RuntimeError(
                "Current state not set (you're probably accessing current state before prompt has started)"
            )
        return self._state

    def set_state(self, prompt_state: PromptState):
        self._state = prompt_state

    @property
    def query(self) -> str:
        return self.state.query

    @property
    def current(self) -> T | None:
        if self.state.current_index is None:
            return None
        return self.entries[self.state.current_index]

    @property
    def current_index(self) -> int | None:
        return self.state.current_index

    @property
    def selections(self) -> list[T]:
        if self.state.selected_count == 0:
            return []
        return [self.entries[i] for i in self.state.target_indices]

    @property
    def selected_indices(self) -> list[int]:
        if self.state.selected_count == 0:
            return []
        return self.state.target_indices

    @property
    def targets(self) -> list[T]:
        """Like with '{+}' fzf placeholder these are selections or current if no selections"""
        return [self.entries[i] for i in self.state.target_indices]

    @property
    def target_indices(self) -> list[int]:
        """Like with '{+n}' fzf placeholder these are indices of selections or current if no selections"""
        return self.state.target_indices

    @property
    def result(self) -> Result[T, S]:
        try:
            return self._result
        except AttributeError as err:
            raise RuntimeError("Result not set") from err

    @property
    def stage(self) -> PromptStage:
        return self._stage

    def set_stage(self, stage: PromptStage):
        self._stage = stage

    def finish(self, trigger: Hotkey | Event, end_status: EndStatus):
        self._result = Result(
            end_status=end_status,
            trigger=trigger,
            entries=self.entries,
            query=self.state.query,
            current_index=self.state.current_index,
            selected_indices=self.selected_indices,
            selections=self.selections,
            target_indices=self.target_indices,
            obj=self.obj,
        )
        self._stage = "finished"

    def fzf_input(self, delimiter: str = "\n") -> str:
        return "".join(f"{self.converter(entry)}{delimiter}" for entry in self.entries)

    def get_current_preview(self) -> str:
        return self.previewer.current_preview.output

    @property
    def automator(self) -> Automator:
        if not self._automator:
            from ..FzfPrompt.automator import Automator

            self._automator = Automator(self)
        return self._automator

    @property
    def controller(self) -> Controller:
        if not self._controller:
            from ..FzfPrompt.controller import Controller

            self._controller = Controller()
        return self._controller

    @property
    def control_port(self) -> int:
        if not self._control_port:
            raise RuntimeError("Control port not set (Are you sure you used Options.listen()?)")
        return self._control_port

    @single_use_method
    def run_initial_setup(self):
        self.previewer.resolve_main_preview(self)
        if self._automator:
            self._automator.prepare()
            self._automator.start()

        def on_startup_success(prompt_data: PromptData, FZF_PORT: str):
            self.set_stage("running")
            if FZF_PORT.isdigit():
                self._control_port = int(FZF_PORT)

        self.action_menu.add(
            "start",
            Binding("On startup success", ServerCall(on_startup_success, command_type="execute-silent")),
            on_conflict="prepend",
        )
        for binding in self.action_menu.bindings.values():
            self.server.add_endpoints(binding)
        self.options += self.action_menu.resolve_options()
        self.options.listen()  # for ServerCalls with FZF_PORT parameter
        self._stage = "ready to run"


class Result[T, S](list[T]):
    def __init__(
        self,
        end_status: EndStatus,
        trigger: Hotkey | Event,
        entries: list[T],
        query: str,
        current_index: int | None,
        selected_indices: list[int],
        selections: list[T],
        target_indices: list[int],
        obj: S,
    ):
        self.end_status: EndStatus = end_status
        self.trigger: Hotkey | Event = trigger
        self.query = query
        self.current_index = current_index  # of pointer starting from 0
        self.current = entries[current_index] if current_index is not None else None
        self.selected_indices = selected_indices  # of marked selections
        self.selections = selections
        self.target_indices = target_indices  # of selections or current if no selections
        self.obj = obj
        super().__init__([entries[i] for i in target_indices])

    def to_dict(self) -> dict:
        return {
            "status": self.end_status,
            "trigger": self.trigger,
            "query": self.query,
            "current_index": self.current_index,
            "current": self.current,
            "selected_indices": self.selected_indices,
            "selections": self.selections,
            "target_indices": self.target_indices,
            "targets": list(self),
            "obj": self.obj,
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, default=repr)


PromptStage = Literal["created", "ready to run", "running", "finished"]


class ChoicesAndLinesMismatch(ValueError): ...
