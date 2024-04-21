from __future__ import annotations

import json
from datetime import datetime

from .action_menu import ActionMenu, Binding, ConflictResolution, ShellCommand
from .automator import Automator
from .decorators import single_use_method
from .options import Hotkey, Options, Situation
from .previewer import GetCurrentPreviewFromServer, Preview, PreviewChange, Previewer, PreviewWindowChange
from .server import EndStatus, PostProcessor, PromptState, ServerCall


class PromptData[T, S]:
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
        self.choices = choices or []
        self.presented_choices = presented_choices or [str(choice) for choice in self.choices]
        self.obj = obj
        self.previewer = previewer or Previewer()
        self.action_menu = action_menu or ActionMenu(self.previewer)
        self.automator = Automator(self.action_menu)
        self.options = options or Options()
        self.post_processors: list[PostProcessor] = []
        self._current_state: PromptState | None = None
        self._result: Result[T]
        self.id = datetime.now().isoformat()  # TODO: Use it?
        self._finished = False

    @property
    def current_state(self) -> PromptState:
        if not self._current_state:
            raise RuntimeError("Current state not set")
        return self._current_state

    def set_current_state(self, prompt_state: PromptState):
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
        self._finished = True

    @property
    def choices_string(self) -> str:
        return "\n".join(self.presented_choices)

    def get_current_preview(self) -> str:
        return self.action_menu.previewer.current_preview.output

    def add_preview(
        self, preview: Preview, *, conflict_resolution: ConflictResolution = "raise error", main: bool = False
    ):
        if preview.hotkey:
            self.action_menu.add(
                preview.hotkey,
                # ❗ It's crucial that window change happens before preview change
                Binding(
                    f"Change preview to '{preview.name}'",
                    PreviewWindowChange(preview.window_size, preview.window_position),
                    PreviewChange(preview),
                    (
                        ShellCommand(preview.command, "change-preview")
                        if not preview.store_output and isinstance(preview.command, str)
                        else GetCurrentPreviewFromServer(preview)
                    ),
                ),
                conflict_resolution=conflict_resolution,
            )
        self.previewer.add(preview, main=main)

    def add_post_processor(self, post_processor: PostProcessor):
        self.post_processors.append(post_processor)

    def apply_common_post_processors(self, prompt_data: PromptData[T, S]):
        for post_processor in self.post_processors:
            post_processor(prompt_data)

    @single_use_method
    def resolve_options(self) -> Options:
        return self.options + self.action_menu.resolve_options() + self.automator.resolve_options()


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
