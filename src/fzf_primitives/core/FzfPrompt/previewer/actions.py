from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, override

if TYPE_CHECKING:
    from ..prompt_data import PromptData
    from .Preview import Preview
from ...monitoring import LoggedComponent
from ..action_menu import ParametrizedAction
from ..options import RelativeWindowSize, WindowPosition
from ..server import CommandOutput, ServerCall, ServerCallFunctionGeneric

type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]
type PreviewChangePreProcessor[T, S] = Callable[[PromptData[T, S], Preview[T, S]], Any]


class SetAsCurrentPreview[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, preview: Preview[T, S], before_change_do: PreviewChangePreProcessor[T, S] | None = None) -> None:
        LoggedComponent.__init__(self)
        self.preview = preview

        def change_current_preview(prompt_data: PromptData[T, S]):
            if before_change_do:
                before_change_do(prompt_data, preview)
            prompt_data.previewer.set_current_preview(preview)
            self.logger.trace(
                f"Changing preview to '{preview.name}'", trace_point="changing_preview", preview=preview.name
            )

        super().__init__(
            change_current_preview, f"SetAsCurrentPreview of {preview.name}", command_type="execute-silent"
        )

    def __str__(self) -> str:
        return f"[SACP]({self.preview.id})"


class PreviewServerCall[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, preview_function: PreviewFunction[T, S], preview: Preview[T, S]) -> None:
        LoggedComponent.__init__(self)
        self.preview = preview
        self.preview_function = preview_function
        super().__init__(preview_function, f"PreviewServerCall of {preview.name}", command_type="change-preview")

        def preview_call(prompt_data: PromptData[T, S], **kwargs):
            output = preview_function(prompt_data, **kwargs)
            if self.preview.store_output:
                self.preview.output = output
            self.logger.trace(
                f"Showing preview '{self.preview.name}'", trace_point="showing_preview", preview=self.preview.name
            )
            return output

        # HACK
        self.function = preview_call

    @property
    @override
    def id(self) -> str:
        return f"{super().id} (preview_id={self.preview.id})"

    def __str__(self) -> str:
        return f"[PSC]({self.id})"


class ShowAndStorePreviewOutput(ServerCall, LoggedComponent):
    def __init__(self, command: str, preview: Preview) -> None:
        LoggedComponent.__init__(self)
        name = f"Store preview output of {preview.name}"
        self._id = f"{name} (preview_id={preview.id}) (command hash {hash(command)})"

        def store_preview_output(prompt_data: PromptData, preview_output: str = CommandOutput("echo $preview_output")):
            preview.output = preview_output
            self.logger.trace(
                f"Storing preview output of '{preview.name}'",
                trace_point="storing_preview_output",
                preview=preview.name,
            )

        super().__init__(store_preview_output, name, "change-preview")
        # HACK ❗
        self.action_value = f'preview_output="$({command})"; echo $preview_output && {self.command}'

    @property
    @override
    def id(self) -> str:
        return self._id

    def __str__(self) -> str:
        return f"[SASPO]({self.id})"


# TODO: Add more --preview-window options
# TODO: How to implement changing only subset of specs? in fzf change-preview-window for unstated specs changes to default
class ChangePreviewWindow(ParametrizedAction):
    def __init__(
        self,
        window_size: int | RelativeWindowSize | None = None,
        window_position: WindowPosition | None = None,
        *,
        line_wrap: bool | None = None,
    ) -> None:
        """window_size: int - absolute, str - relative and should be in '<int>%' format (99% max)"""
        self.window_size: int | RelativeWindowSize | None = window_size
        self.window_position: WindowPosition | None = window_position
        self.line_wrap = line_wrap
        super().__init__(
            ",".join(
                val
                for val in (str(self.window_size), self.window_position, "wrap" if self.line_wrap else "nowrap")
                if val is not None
            ),
            "change-preview-window",
        )

    def __str__(self) -> str:
        return f"[CPW]({self.action_value})"

    # TODO: Use it to change only subset of specs
    def __add__(self, other: ChangePreviewWindow) -> ChangePreviewWindow:
        return ChangePreviewWindow(
            window_size=other.window_size if other.window_size is not None else self.window_size,
            window_position=other.window_position if other.window_position is not None else self.window_position,
            line_wrap=other.line_wrap if other.line_wrap is not None else self.line_wrap,
        )


# TODO
#     def __or__(self, other: ChangePreviewWindow) -> CyclicalChangePreviewWindow:
#         return CyclicalChangePreviewWindow(self, other)


# class CyclicalChangePreviewWindow(ChangePreviewWindow):
#     def __init__(self, *window_changes: ChangePreviewWindow) -> None:
#         self.window_changes = list(window_changes)

#     def __or__(self, other: ChangePreviewWindow) -> CyclicalPreviewWindow:
#         self.window_changes.append(other)
#         return self

#     def __ror__(self, other: ChangePreviewWindow) -> CyclicalPreviewWindow:
#         self.window_changes.insert(0, other)
#         return self


class ChangePreviewLabel(ParametrizedAction):
    def __init__(self, label: str) -> None:
        super().__init__(label, "change-preview-label")

    def __str__(self) -> str:
        return f"[CPL]({self.action_value})"
