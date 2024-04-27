from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .prompt_data import PromptData
from ..monitoring import Logger
from .action_menu import Action, ActionMenu, Binding, ConflictResolution, ParametrizedAction, ShellCommand
from .options import Hotkey, Position, RelativeWindowSize, Situation
from .server import CommandOutput, ServerCall, ServerCallFunctionGeneric

logger = Logger.get_logger()

type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]
type PreviewChangePreProcessor[T, S] = Callable[[PromptData[T, S], Preview[T, S]], Any]


class Preview[T, S]:
    # TODO: line wrap
    def __init__(
        self,
        name: str,
        command: str | PreviewFunction[T, S],
        event: Hotkey | Situation | None = None,
        window_size: int | RelativeWindowSize = "50%",
        window_position: Position = "right",
        label: str = "",
        before_change_do: PreviewChangePreProcessor[T, S] | None = None,
        *,
        line_wrap: bool = True,
        store_output: bool = True,
    ):
        self.name = name
        self.id = f"{name} ({id(self)})"
        self.command = command
        self.event: Hotkey | Situation | None = event
        self.window_size: int | RelativeWindowSize = window_size
        self.window_position: Position = window_position
        self.label = label
        self.line_wrap = line_wrap
        self.store_output = store_output
        self._output: str | None = None

        # ❗ It's crucial that window change happens before preview change
        actions: list[Action] = [
            PreviewWindowChange(window_size, window_position, line_wrap=line_wrap),
            PreviewChange(self, before_change_do),
            (
                (
                    StorePreviewOutput(self.command, self)
                    if store_output
                    else ShellCommand(self.command, "change-preview")
                )
                if isinstance(self.command, str)
                else InvokeCurrentPreview(self.command, self)
            ),
            PreviewLabelChange(label),
        ]
        self.preview_change_binding = Binding(f"Change preview to '{name}'", *actions)

    @property
    def output(self) -> str:
        if self._output is None:
            if self.store_output:
                raise RuntimeError("Output not set")
            raise Warning("Output not stored for this preview")
        return self._output

    @output.setter
    def output(self, value: str):
        self._output = value


class PreviewChange(ServerCall):
    def __init__(self, preview: Preview, before_change_do: PreviewChangePreProcessor | None = None) -> None:

        def change_current_preview(prompt_data: PromptData):
            if before_change_do:
                before_change_do(prompt_data, preview)
            prompt_data.previewer.set_current_preview(preview.id)
            logger.trace(f"Changing preview to '{preview.name}'", preview=preview.name)

        super().__init__(change_current_preview, command_type="execute-silent")


class InvokeCurrentPreview(ServerCall):
    def __init__(self, preview_function: PreviewFunction, preview: Preview) -> None:
        action_type = "change-preview"

        def get_current_preview(prompt_data: PromptData, **kwargs):
            preview.output = preview_function(prompt_data)
            logger.trace(f"Showing preview '{preview.name}'", preview=preview.name)
            return preview.output

        super().__init__(preview_function, f"Show preview of {preview.name}", command_type=action_type)
        # HACK: wanna ServerCall to parse parameters of enclosed function first to create the right template
        self.function = get_current_preview


class StorePreviewOutput(ServerCall):
    def __init__(self, preview_command: str, preview: Preview) -> None:

        def store_preview_output(prompt_data: PromptData, preview_output: str = CommandOutput("echo $preview_output")):
            preview.output = preview_output
            logger.trace(f"Showing preview '{preview.name}'", preview=preview.name)

        super().__init__(store_preview_output, f"Store preview of {preview.name}", "change-preview")
        # HACK ❗
        self.action_value = f'preview_output="$({preview_command})"; echo $preview_output && {self.command}'


class PreviewWindowChange(ParametrizedAction):
    def __init__(
        self, window_size: int | RelativeWindowSize, window_position: Position, *, line_wrap: bool = True
    ) -> None:
        """Window size: int - absolute, str - relative and should be in '<int>%' format"""
        self.window_size = window_size
        self.window_position = window_position
        super().__init__(
            f"{self.window_size},{self.window_position}:{'wrap' if line_wrap else 'nowrap'}", "change-preview-window"
        )


class PreviewLabelChange(ParametrizedAction):
    def __init__(self, label: str) -> None:
        super().__init__(label, "change-preview-label")


class Previewer[T, S]:
    """Handles storing preview outputs and tracking current preview and possibly other logic associated with previews"""

    def __init__(self, action_menu: ActionMenu) -> None:
        self._previews: dict[str, Preview[T, S]] = {}
        self._current_preview: Preview[T, S] | None = None
        self._action_menu = action_menu

    @property
    def current_preview(self) -> Preview[T, S]:
        if not self._current_preview:
            raise RuntimeError("No current preview set")
        return self._current_preview

    def set_current_preview(self, preview_id: str):
        self._current_preview = self.get_preview(preview_id)

    def get_preview(self, preview_id: str) -> Preview[T, S]:
        return self._previews[preview_id]

    @property
    def previews(self) -> list[Preview[T, S]]:
        return list(self._previews.values())

    def add(
        self, preview: Preview[T, S], *, conflict_resolution: ConflictResolution = "raise error", main: bool = False
    ):
        logger.debug(f"📺 Adding preview '{preview.name}'")
        if main or not self._previews:
            self._current_preview = preview
        self._previews[preview.id] = preview
        if preview.event:
            self._action_menu.add(
                preview.event, preview.preview_change_binding, conflict_resolution=conflict_resolution
            )
        else:
            self._action_menu.add_server_calls(preview.preview_change_binding)

    def resolve_main_preview(self, prompt_data: PromptData[T, S]):
        if self._current_preview:
            self._action_menu.add("start", self._current_preview.preview_change_binding, conflict_resolution="prepend")
