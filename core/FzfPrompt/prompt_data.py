from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .automator import Automator
from ..monitoring import LoggedComponent
from .action_menu import ActionMenu, Binding
from .controller import Controller
from .decorators import single_use_method
from .options import Hotkey, Options, Situation
from .previewer import Previewer
from .server import EndStatus, PostProcessor, PromptState, Server, ServerCall
from .server.make_server_call import make_server_call


class PromptData[T, S](LoggedComponent):
    """Accessed from fzf process through socket Server"""

    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        previewer: Previewer[T, S] | None = None,
        action_menu: ActionMenu[T, S] | None = None,
        options: Options | None = None,
    ):
        super().__init__()
        self.logger.debug("PromptData created")
        self.choices = choices or []
        self.presented_choices = presented_choices or [str(choice) for choice in self.choices]
        self.check_choices_and_lines_length(self.choices, self.presented_choices)
        self.obj = obj
        self.action_menu = action_menu or ActionMenu()
        self.server = Server(self)
        self.previewer = previewer or Previewer()
        self._automator: Automator | None = None
        self._controller: Controller | None = None
        self.bindings_to_automate: list[Binding] = []
        self.options = options or Options()
        self.post_processors: list[PostProcessor] = []
        self._current_state: PromptState | None = None
        self._result: Result[T]
        self.id = datetime.now().isoformat()  # TODO: Use it?
        self.run_vars: dict[str, Any] = {"env": os.environ.copy()}
        self._stage: PromptStage = "created"
        self._control_port: int | None = None
        self.make_server_call = make_server_call

    @property
    def current_state(self) -> PromptState:
        if not self._current_state:
            raise RuntimeError(
                "Current state not set (you're probably accessing current state before prompt has started)"
            )
        return self._current_state

    def set_current_state(self, prompt_state: PromptState):
        self._current_state = prompt_state

    @property
    def current_single_choice(self) -> T | None:
        if self.current_state.single_index is None:
            return None
        return self.choices[self.current_state.single_index]

    @property
    def current_choices(self) -> list[T]:
        return [self.choices[i] for i in self.current_state.indices]

    @property
    def result(self) -> Result[T]:
        try:
            return self._result
        except AttributeError as err:
            raise RuntimeError("Result not set") from err

    @property
    def stage(self) -> PromptStage:
        return self._stage

    def set_stage(self, stage: PromptStage):
        self._stage = stage

    def finish(self, event: Hotkey | Situation, end_status: EndStatus):
        self._result = Result(
            end_status=end_status,
            event=event,
            choices=self.choices,
            query=self.current_state.query,
            single_index=self.current_state.single_index,
            indices=self.current_state.indices,
            single_line=self.current_state.single_line,
            lines=self.current_state.lines,
        )
        self._stage = "finished"

    @property
    def choices_string(self) -> str:
        return "\n".join(self.presented_choices)

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

    def check_choices_and_lines_length(self, choices: list, lines: list):
        if len(choices) != len(lines):
            message = f"Choices and lines have different lengths: {len(choices)} vs {len(lines)}"
            raise ChoicesAndLinesMismatch(message)


class Result[T](list[T]):
    def __init__(
        self,
        end_status: EndStatus,
        event: Hotkey | Situation,
        choices: list[T],
        query: str,  # as in {q} placeholder
        single_index: int | None,  # as in {n} placeholder
        indices: list[int],  # as in {+n} placeholder
        single_line: str | None,  # as in {} placeholder; stripped of ANSI codes
        lines: list[str],  # as in {+} placeholder; stripped of ANSI codes
    ):
        self.end_status: EndStatus = end_status
        self.event: Hotkey | Situation = event
        self.query = query
        self.single_index = single_index  # of pointer starting from 0
        self.indices = indices  # of marked selections or pointer if none are selected
        self.single = choices[single_index] if single_index is not None else None
        self.single_line = single_line  # pointed at
        self.lines = lines  # marked selections or pointer if none are selected
        super().__init__([choices[i] for i in indices])

    def __str__(self) -> str:
        return json.dumps(
            {
                "status": self.end_status,
                "event": self.event,
                "query": self.query,
                "single_index": self.single_index,
                "indices": self.indices,
                "selections": list(self),
                "single": self.single,
                "single_line": self.single_line,
                "lines": self.lines,
            },
            indent=4,
            default=repr,
        )


PromptStage = Literal["created", "ready to run", "running", "finished"]


class ChoicesAndLinesMismatch(ValueError): ...
