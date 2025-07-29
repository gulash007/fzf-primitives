from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypedDict, Unpack

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ..action_menu import Binding, ShellCommand, Transform
from ..options import RelativeWindowSize, WindowPosition
from ..server import ServerCallFunctionGeneric
from .actions import (
    ChangePreviewLabel,
    ChangePreviewWindow,
    PreviewServerCall,
    SetAsCurrentPreview,
    ShowAndStorePreviewOutput,
)

type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]
type PreviewChangePreProcessor[T, S] = Callable[[PromptData[T, S], Preview[T, S]], Any]
type PreviewMutator[T, S] = Callable[[PromptData[T, S]], PreviewMutationArgs[T, S]]


# TODO: Add defaults to Config?
class PreviewStyleMutationArgs(TypedDict, total=False):
    window_size: int | RelativeWindowSize
    window_position: WindowPosition
    line_wrap: bool


class PreviewMutationArgs[T, S](PreviewStyleMutationArgs, total=False):
    output_generator: str | PreviewFunction[T, S]
    label: str
    before_change_do: PreviewChangePreProcessor[T, S]
    store_output: bool


DEFAULT_OUTPUT_GENERATOR = ""
DEFAULT_WINDOW_SIZE = "50%"
DEFAULT_WINDOW_POSITION = "right"
DEFAULT_LABEL = ""
DEFAULT_LINE_WRAP = True
DEFAULT_BEFORE_CHANGE_DO = lambda pd, preview: None
DEFAULT_STORE_OUTPUT = True


class Preview[T, S]:
    # TODO: line wrap
    def __init__(self, name: str, **kwargs: Unpack[PreviewMutationArgs[T, S]]):
        self.name = name
        self.id = f"{name}#{id(self)}"
        self.output_generator = kwargs.get("output_generator", DEFAULT_OUTPUT_GENERATOR)
        self.window_size: int | RelativeWindowSize = kwargs.get("window_size", DEFAULT_WINDOW_SIZE)
        self.window_position: WindowPosition = kwargs.get("window_position", DEFAULT_WINDOW_POSITION)
        self.label = kwargs.get("label", DEFAULT_LABEL)
        self.line_wrap = kwargs.get("line_wrap", DEFAULT_LINE_WRAP)
        self.before_change_do = kwargs.get("before_change_do", DEFAULT_BEFORE_CHANGE_DO)
        self.store_output = kwargs.get("store_output", DEFAULT_STORE_OUTPUT)
        self._output: str | None = None

        # Using a Transform so that mutations of Preview are expressed when switching to it using just its basic binding
        self._create_new_actions()
        self.transform_preview = Transform[T, S](
            # ❗ It's crucial that window change happens before creating output
            lambda pd: (
                self.set_as_current_preview,
                self.change_preview_window,
                self.change_preview_output,
                self.change_preview_label,
            ),
            f"Change preview to {name}",
        )
        self.preview_change_binding = Binding(f"Change preview to {name}", self.transform_preview)

    @property
    def set_as_current_preview(self):
        return self._set_as_current_preview

    @property
    def change_preview_window(self):
        return self._change_preview_window

    @property
    def change_preview_output(self):
        return self._change_preview_output

    @property
    def change_preview_label(self):
        return self._change_preview_label

    def _create_new_actions(self):
        self._set_as_current_preview = SetAsCurrentPreview(self, self.before_change_do)
        self._change_preview_window = ChangePreviewWindow(
            self.window_size, self.window_position, line_wrap=self.line_wrap
        )
        self._change_preview_output = (
            get_preview_shell_command(self.output_generator, self)
            if isinstance(self.output_generator, str)
            else PreviewServerCall(self.output_generator, self)
        )
        self._change_preview_label = ChangePreviewLabel(self.label)

    def update(self, **kwargs: Unpack[PreviewMutationArgs[T, S]]):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._create_new_actions()

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

    @property
    def mutation_args(self) -> PreviewMutationArgs[T, S]:
        return PreviewMutationArgs(
            output_generator=self.output_generator,
            window_size=self.window_size,
            window_position=self.window_position,
            label=self.label,
            line_wrap=self.line_wrap,
            before_change_do=self.before_change_do,
            store_output=self.store_output,
        )

    def __str__(self) -> str:
        return f"[Preview]({self.id})"


def get_preview_shell_command(command: str, preview: Preview):
    if preview.store_output:
        return ShowAndStorePreviewOutput(command, preview)
    return ShellCommand(command)
