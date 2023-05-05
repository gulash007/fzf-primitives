from __future__ import annotations

from dataclasses import dataclass, field
from string import Template
from typing import TYPE_CHECKING, Callable, Generic, Literal, Protocol, Self, Type, TypeVar

from .ActionMenu import Action
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


PRESET_PREVIEWS = {
    "basic": "/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/.env/bin/python3.11 -m fzf_primitives.experimental.core.actions.preview_basic {q} {} {+}"
}


@dataclass
class Preview:
    id: str
    command: str | None
    hotkey: Hotkey
    window_size: int | str = "50%"
    window_position: Position = "right"

    # TODO: Use it to do actions on it (clip, lightspeed highlight)
    output: str | None = field(init=False, default=None)

    # function: PreviewFunction | None = None

    def __post_init__(self):
        if self.command is None:
            self.command = PRESET_PREVIEWS.get(self.id)

    def __call__(self, func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.add_preview(self)
            return func(prompt_data, *args, **kwargs)

        return with_preview

    def server_call(self) -> ServerCall:
        server_call = ServerCall(f"Change preview to '{self.id}'", self.change_preview, self.hotkey)
        server_call.unformatted_command = Template(
            f"change-preview({self.command})"
            f"+change-preview-window({self.window_size},{self.window_position})"
            "+refresh-preview"
            f"+{server_call.unformatted_command.template}"
        )
        return server_call

    def change_preview(self, prompt_data: PromptData):
        prompt_data.previewer.main_preview = self


class Previewer:
    """Handles passing right preview options"""

    def __init__(self) -> None:
        self.previews: dict[str, Preview] = {}
        self.main_preview: Preview | None = None

    def add_preview(self, preview: Preview, main=False):
        if main or self.main_preview is None:
            self.main_preview = preview
        self.previews[preview.id] = preview

    def resolve_options(self) -> Options:  # TODO: socket number
        if self.main_preview is None:
            return Options()
        if self.main_preview.command is None:
            raise RuntimeError("Preview has no command")
        options = (
            Options()
            .preview(self.main_preview.command)
            .add(f"--preview-window={self.main_preview.window_position},{self.main_preview.window_size}")
        )

        # for preview_name, preview in self.previews.items(): # TODO: attach change preview hotkey
        #     options.bind(preview.hotkey, f"execute({RequestCommand(preview_name, socket_number)})")
        return options
