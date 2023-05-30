from __future__ import annotations

from dataclasses import dataclass, field
from string import Template
from typing import TYPE_CHECKING, Callable, Generic, Literal, Protocol, Self, Type, TypeVar

from .ActionMenu import Action, ActionMenu, ParametrizedAction, ShellCommand
from .commands.fzf_placeholders import PLACEHOLDERS
from .Server import ServerCall

if TYPE_CHECKING:
    from .PromptData import PromptData
    from ..mods import Moddable, P

from ..actions.functions import preview_basic
from .options import Hotkey, Options, Position


class PreviewFunction(Protocol):
    @staticmethod
    def __call__(query: str, selection: str, selections: list[str]) -> str:
        ...


PREVIEW_FUNCTIONS = {"no preview": lambda *args, **kwargs: None, "basic": preview_basic}


@dataclass
class Preview:
    name: str
    command: ShellCommand
    hotkey: Hotkey  # TODO: | Event
    window_size: int | str = "50%"
    window_position: Position = "right"
    preview_label: str | None = None

    # TODO: Use it to do actions on it (clip, lightspeed highlight)
    output: str | None = field(init=False, default=None)

    # function: PreviewFunction | None = None

    def get_store_output_server_call(self):
        return

    def store_output_action(self) -> Action:
        return Action(f"Store '{self.name}'", ServerCall(self.store_output), self.hotkey)

    def store_output(self, prompt_data: PromptData, preview_name: str, preview_output: str):
        prompt_data.previewer.previews[preview_name].output = preview_output

    def change_preview(self, prompt_data: PromptData):
        prompt_data.previewer.current_preview = self


class PreviewChange(ParametrizedAction):
    def __init__(self, preview: Preview) -> None:
        self.shell_command = preview.command

    def __str__(self) -> str:
        return f"change-preview({self.shell_command})"


class PreviewWindowChange(ParametrizedAction):
    def __init__(self, window_size: int | str, window_position: Position) -> None:
        self.window_size = window_size
        self.window_position = window_position

    def __str__(self) -> str:
        return f"change-preview-window({self.window_size},{self.window_position})"


class Previewer:
    """Handles passing right preview options"""

    def __init__(self) -> None:
        self.previews: dict[str, Preview] = {}
        self.current_preview: Preview | None = None

    def add(self, preview: Preview, action_menu: ActionMenu, main: bool = False):
        if main or self.current_preview is None:
            self.current_preview = preview
        self.previews[preview.name] = preview
        action_menu.add(
            f"Change preview to '{preview.name}'",
            preview.hotkey,
            PreviewChange(preview),
            PreviewWindowChange(preview.window_size, preview.window_position),
            "refresh-preview",
        )

    def resolve_options(self) -> Options:
        if self.current_preview is None:
            return Options()
        if self.current_preview.command is None:
            raise RuntimeError("Preview has no command")
        options = (
            Options()
            .preview(str(self.current_preview.command))
            .add(f"--preview-window={self.current_preview.window_position},{self.current_preview.window_size}")
        )

        # for preview_name, preview in self.previews.items(): # TODO: attach change preview hotkey
        #     options.bind(preview.hotkey, f"execute({RequestCommand(preview_name, socket_number)})")
        return options
