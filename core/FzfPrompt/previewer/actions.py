from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, override

if TYPE_CHECKING:
    from ..prompt_data import PromptData
    from .Preview import Preview
from ...monitoring import LoggedComponent
from ..action_menu import ParametrizedAction
from ..options import RelativeWindowSize, WindowPosition
from ..server import CommandOutput, Request, ServerCall, ServerCallFunctionGeneric

type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]
type PreviewChangePreProcessor[T, S] = Callable[[PromptData[T, S], Preview[T, S]], Any]


class SetAsCurrentPreview[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, preview: Preview[T, S], before_change_do: PreviewChangePreProcessor[T, S] | None = None) -> None:
        LoggedComponent.__init__(self)

        def change_current_preview(prompt_data: PromptData[T, S]):
            if before_change_do:
                before_change_do(prompt_data, preview)
            prompt_data.previewer.set_current_preview(preview)
            self.logger.trace(f"Changing preview to '{preview.name}'", preview=preview.name)

        super().__init__(change_current_preview, command_type="execute-silent")


class PreviewServerCall[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, preview_function: PreviewFunction[T, S], preview: Preview[T, S]) -> None:
        LoggedComponent.__init__(self)
        self.preview = preview
        super().__init__(preview_function, f"Resolve preview function of {preview.name}", command_type="change-preview")

    @property
    @override
    def id(self) -> str:
        return f"{super().id} (preview_id={self.preview.id})"

    @override
    def run(self, prompt_data: PromptData[T, S], request: Request):
        output = super().run(prompt_data, request)
        if self.preview.store_output:
            self.preview.output = output
        self.logger.trace(f"Showing preview '{self.preview.name}'", preview=self.preview.name)
        return output


class ShowAndStorePreviewOutput(ServerCall, LoggedComponent):
    def __init__(self, command: str, preview: Preview) -> None:
        LoggedComponent.__init__(self)
        name = f"Store preview of {preview.name}"
        self._id = f"{name} (preview_id={preview.id}) (command hash {hash(command)})"

        def store_preview_output(prompt_data: PromptData, preview_output: str = CommandOutput("echo $preview_output")):
            preview.output = preview_output
            self.logger.trace(f"Storing preview output of '{preview.name}'", preview=preview.name)

        super().__init__(store_preview_output, name, "change-preview")
        # HACK ❗
        self.action_value = f'preview_output="$({command})"; echo $preview_output && {self.command}'

    @property
    @override
    def id(self) -> str:
        return self._id


# TODO: Add more --preview-window options
class ChangePreviewWindow(ParametrizedAction):
    def __init__(
        self,
        window_size: int | RelativeWindowSize | None = None,
        window_position: WindowPosition | None = None,
        *,
        line_wrap: bool | None = None,
    ) -> None:
        """window_size: int - absolute, str - relative and should be in '<int>%' format (99% max)"""
        self.window_size = window_size
        self.window_position = window_position
        self.line_wrap = line_wrap
        super().__init__(
            ",".join(
                val
                for val in (str(self.window_size), self.window_position, "wrap" if self.line_wrap else "nowrap")
                if val is not None
            ),
            "change-preview-window",
        )


class ChangePreviewLabel(ParametrizedAction):
    def __init__(self, label: str) -> None:
        super().__init__(label, "change-preview-label")
