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
        self.id = f"{name} ({id(self)})"
        self.output_generator = kwargs.get("output_generator", DEFAULT_OUTPUT_GENERATOR)
        self.window_size: int | RelativeWindowSize = kwargs.get("window_size", DEFAULT_WINDOW_SIZE)
        self.window_position: WindowPosition = kwargs.get("window_position", DEFAULT_WINDOW_POSITION)
        self.label = kwargs.get("label", DEFAULT_LABEL)
        self.line_wrap = kwargs.get("line_wrap", DEFAULT_LINE_WRAP)
        self.before_change_do = kwargs.get("before_change_do", DEFAULT_BEFORE_CHANGE_DO)
        self.store_output = kwargs.get("store_output", DEFAULT_STORE_OUTPUT)
        self._output: str | None = None

        # Using a Transform so that mutations of Preview are expressed when switching to it using just its basic binding
        self.transform_preview = Transform[T, S](
            # ❗ It's crucial that window change happens before creating output
            lambda pd: (
                SetAsCurrentPreview(self, self.before_change_do),
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


def get_preview_shell_command(command: str, preview: Preview):
    if preview.store_output:
        return ShowAndStorePreviewOutput(command, preview)
    return ShellCommand(command)
