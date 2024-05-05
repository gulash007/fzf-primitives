from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypedDict, Unpack, override

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..action_menu import Binding, ParametrizedAction, ShellCommand, Transformation
from ..options import WindowPosition, RelativeWindowSize
from ..server import CommandOutput, Request, ServerCall, ServerCallFunctionGeneric

type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]
type PreviewChangePreProcessor[T, S] = Callable[[PromptData[T, S], Preview[T, S]], Any]


class Preview[T, S]:
    # TODO: line wrap
    def __init__(
        self,
        name: str,
        output_generator: str | PreviewFunction[T, S],
        window_size: int | RelativeWindowSize = "50%",
        window_position: WindowPosition = "right",
        label: str = "",
        before_change_do: PreviewChangePreProcessor[T, S] | None = None,
        *,
        line_wrap: bool = True,
        store_output: bool = True,
    ):
        self.name = name
        self.id = f"{name} ({id(self)})"
        self.output_generator = output_generator
        self.window_size: int | RelativeWindowSize = window_size
        self.window_position: WindowPosition = window_position
        self.label = label
        self.line_wrap = line_wrap
        self.store_output = store_output
        self._output: str | None = None

        set_current_preview = SetAsCurrentPreview(self, before_change_do)
        self.transform_preview = Transformation[T, S](
            # ❗ It's crucial that window change happens before creating output
            lambda pd: (
                set_current_preview,
                ChangePreviewWindow(self.window_size, self.window_position, line_wrap=self.line_wrap),
                get_preview_shell_command(self.output_generator, self)
                if isinstance(self.output_generator, str)
                else PreviewServerCall(self.output_generator, self),
                ChangePreviewLabel(self.label),
            )
        )
        self.preview_change_binding = Binding(f"Change preview to {name}", self.transform_preview)

    def update(self, **kwargs: Unpack[PreviewMutationArgs[T, S]]):
        for key, value in kwargs.items():
            setattr(self, key, value)

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


type PreviewMutator[T, S] = Callable[[PromptData[T, S]], PreviewMutationArgs[T, S]]


class PreviewMutationArgs[T, S](TypedDict, total=False):
    name: str
    output_generator: str | PreviewFunction[T, S]
    window_size: int | RelativeWindowSize
    window_position: WindowPosition
    label: str
    line_wrap: bool
    store_output: bool


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


def get_preview_shell_command(command: str, preview: Preview):
    if preview.store_output:
        return ShowAndStorePreviewOutput(command, preview)
    return ShellCommand(command)


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


class ChangePreviewWindow(ParametrizedAction):
    def __init__(
        self, window_size: int | RelativeWindowSize, window_position: WindowPosition, *, line_wrap: bool = True
    ) -> None:
        """Window size: int - absolute, str - relative and should be in '<int>%' format"""
        self.window_size = window_size
        self.window_position = window_position
        super().__init__(
            f"{self.window_size},{self.window_position}:{'wrap' if line_wrap else 'nowrap'}", "change-preview-window"
        )


class ChangePreviewLabel(ParametrizedAction):
    def __init__(self, label: str) -> None:
        super().__init__(label, "change-preview-label")
