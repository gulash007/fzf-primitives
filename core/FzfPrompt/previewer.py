from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .prompt_data import PromptData
from ..monitoring import Logger
from .action_menu.binding import Binding
from .action_menu.parametrized_actions import Action, ParametrizedAction, ShellCommand
from .options import Hotkey, Position, RelativeWindowSize, Situation
from .server import CommandOutput, ServerCall, ServerCallFunctionGeneric

logger = Logger.get_logger()

type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]


class Preview[T, S]:
    # TODO: | Event
    # TODO: line wrap
    def __init__(
        self,
        name: str,
        command: str | PreviewFunction[T, S],
        event: Hotkey | Situation | None = None,
        window_size: int | RelativeWindowSize = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        self.name = name
        self.id = f"{name} ({id(self)})"
        self.command = command
        self.event: Hotkey | Situation | None = event
        self.window_size: int | RelativeWindowSize = window_size
        self.window_position: Position = window_position
        self.preview_label = preview_label
        self.store_output = store_output
        self._output: str | None = None

        # ❗ It's crucial that window change happens before preview change
        actions: list[Action] = [PreviewWindowChange(window_size, window_position)]
        if preview_label:
            actions.append(PreviewLabelChange(preview_label))
        actions.append(PreviewChange(self))
        actions.append(
            ShellCommand(command, "change-preview")
            if not store_output and isinstance(command, str)
            else GetCurrentPreviewFromServer(self)
        )
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
    def __init__(self, preview: Preview) -> None:

        def change_current_preview(prompt_data: PromptData):
            prompt_data.previewer.set_current_preview(preview.id)
            logger.trace(f"Changing preview to '{preview.name}'", preview=preview.name)

        super().__init__(change_current_preview, action_type="execute-silent")


class GetCurrentPreviewFromServer(ServerCall):
    def __init__(self, preview: Preview) -> None:
        action_type = "change-preview"
        command = preview.command
        if isinstance(command, str):

            def store_preview_output(
                prompt_data: PromptData, preview_output: str = CommandOutput("echo $preview_output")
            ):
                preview.output = preview_output
                logger.trace(f"Showing preview '{preview.name}'", preview=preview.name)

            super().__init__(store_preview_output, f"Store preview of {preview.name}", action_type)
            self.template = f'preview_output="$({preview.command})"; echo $preview_output && {self.template}'

        else:

            def get_current_preview(prompt_data: PromptData, **kwargs):
                preview.output = command(prompt_data)
                logger.trace(f"Showing preview '{preview.name}'", preview=preview.name)
                return preview.output

            super().__init__(command, f"Show preview of {preview.name}", action_type=action_type)
            # HACK: wanna ServerCall to parse parameters of enclosed function first to create the right template
            self.function = get_current_preview


class PreviewWindowChange(ParametrizedAction):
    def __init__(self, window_size: int | RelativeWindowSize, window_position: Position) -> None:
        """Window size: int - absolute, str - relative and should be in '<int>%' format"""
        self.window_size = window_size
        self.window_position = window_position
        super().__init__(f"{self.window_size},{self.window_position}", "change-preview-window")


class PreviewLabelChange(ParametrizedAction):
    def __init__(self, label: str) -> None:
        super().__init__(label, "change-preview-label")


class Previewer[T, S]:
    """Handles storing preview outputs and tracking current preview and possibly other logic associated with previews"""

    def __init__(self) -> None:
        self._previews: dict[str, Preview[T, S]] = {}
        self._current_preview: Preview[T, S] | None = None

    @property
    def current_preview(self) -> Preview[T, S]:
        if not self._current_preview:
            raise RuntimeError("No current preview set")
        return self._current_preview

    def set_current_preview(self, preview_id: str):
        self._current_preview = self.get_preview(preview_id)

    @property
    def previews(self) -> list[Preview[T, S]]:
        return list(self._previews.values())

    def add(self, preview: Preview[T, S], *, main: bool = False):
        if main or not self._previews:
            self._current_preview = preview
        self._previews[preview.id] = preview

    def get_preview(self, preview_id: str) -> Preview[T, S]:
        return self._previews[preview_id]
