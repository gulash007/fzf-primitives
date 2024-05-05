from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypedDict, Unpack

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ..action_menu import Binding, ShellCommand, Transformation
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


def get_preview_shell_command(command: str, preview: Preview):
    if preview.store_output:
        return ShowAndStorePreviewOutput(command, preview)
    return ShellCommand(command)
