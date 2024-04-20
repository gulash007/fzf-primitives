from __future__ import annotations

import json
from datetime import datetime

from . import action_menu as am
from . import automator as auto
from . import decorators as dec
from . import options as op
from . import previewer as pv
from . import server as sv


class PromptData[T, S]:
    """Accessed from fzf process through socket Server"""

    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        previewer: pv.Previewer[T, S] | None = None,
        action_menu: am.ActionMenu[T, S] | None = None,
        options: op.Options | None = None,
    ):
        self.choices = choices or []
        self.presented_choices = presented_choices or [str(choice) for choice in self.choices]
        self.obj = obj
        self.previewer = previewer or pv.Previewer()
        self.action_menu = action_menu or am.ActionMenu(self.previewer)
        self.automator = auto.Automator()
        self.options = options or op.Options()
        self.post_processors: list[sv.PostProcessor] = []
        self._current_state: sv.PromptState | None = None
        self._result: Result[T]
        self.id = datetime.now().isoformat()  # TODO: Use it?
        self._finished = False

    @property
    def current_state(self) -> sv.PromptState:
        if not self._current_state:
            raise RuntimeError("Current state not set")
        return self._current_state

    def set_current_state(self, prompt_state: sv.PromptState):
        self._current_state = prompt_state

    @property
    def result(self) -> Result[T]:
        try:
            return self._result
        except AttributeError as err:
            raise RuntimeError("Result not set") from err

    @property
    def finished(self) -> bool:
        return self._finished

    def finish(self, event: am.Hotkey | am.Situation, end_status: sv.EndStatus):
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
        self._finished = True

    @property
    def choices_string(self) -> str:
        return "\n".join(self.presented_choices)

    def get_current_preview(self) -> str:
        return self.action_menu.previewer.current_preview.output

    def add_preview(
        self, preview: pv.Preview, *, conflict_resolution: am.ConflictResolution = "raise error", main: bool = False
    ):
        if preview.hotkey:
            self.action_menu.add(
                preview.hotkey,
                # ❗ It's crucial that window change happens before preview change
                am.Binding(
                    f"Change preview to '{preview.name}'",
                    pv.PreviewWindowChange(preview.window_size, preview.window_position),
                    pv.PreviewChange(preview),
                    (
                        am.ShellCommand(preview.command, "change-preview")
                        if not preview.store_output and isinstance(preview.command, str)
                        else pv.GetCurrentPreviewFromServer(preview)
                    ),
                ),
                conflict_resolution=conflict_resolution,
            )
        self.previewer.add(preview, main=main)

    def add_post_processor(self, post_processor: sv.PostProcessor):
        self.post_processors.append(post_processor)

    def apply_common_post_processors(self, prompt_data: PromptData[T, S]):
        for post_processor in self.post_processors:
            post_processor(prompt_data)

    @dec.single_use_method
    def resolve_options(self) -> op.Options:
        return self.options + self.action_menu.resolve_options()

    def server_calls(self) -> list[sv.ServerCall]:
        server_calls = [action for action in self.action_menu.actions if isinstance(action, sv.ServerCall)]
        if self.action_menu.should_run_automator:
            return [*server_calls, self.automator.move_to_next_binding_server_call]
        return server_calls


class Result[T](list[T]):
    def __init__(
        self,
        end_status: sv.EndStatus,
        event: am.Hotkey | am.Situation,
        choices: list[T],
        query: str,  # as in {q} placeholder
        single_index: int | None,  # as in {n} placeholder
        indices: list[int],  # as in {+n} placeholder
        single_line: str | None,  # as in {} placeholder; stripped of ANSI codes
        lines: list[str],  # as in {+} placeholder; stripped of ANSI codes
    ):
        self.end_status: sv.EndStatus = end_status
        self.event: am.Hotkey | am.Situation = event
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
