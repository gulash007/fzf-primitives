from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Literal, Protocol, Self, Type, TypeVar

if TYPE_CHECKING:
    from .PromptData import PromptData
    from ..mods import Moddable, P

from pydantic import BaseModel

from ..actions.functions import preview_basic
from .options import Hotkey, Options, Position


class PreviewFunction(Protocol):
    @staticmethod
    def __call__(query: str, selection: str, selections: list[str]) -> str:
        ...


PREVIEW_FUNCTIONS = {"no preview": lambda *args, **kwargs: None, "basic": preview_basic}


class Preview:
    def __init__(
        self,
        id_: str,
        command: str | None = None,
        output: str | None = None,
        window_size: int | str = "50%",
        window_position: Position = "right",
    ) -> None:
        self.id = id_
        self.command = command
        # hotkey: Hotkey
        self.output = output  # TODO: Use it to do actions on it (clip, lightspeed highlight)
        self.window_size = window_size
        self.window_position = window_position

    # function: PreviewFunction | None = None
    # command: str | None = None

    def __call__(self, func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.add_preview(self)
            return func(
                prompt_data,
                *args,
                **kwargs,
            )

        return with_preview

    def run_function(self, query, *selections):
        output = PREVIEW_FUNCTIONS[self.id](query, selections)
        self.output = output
        return output

    def update(self, query, selections):
        self.output = PREVIEW_FUNCTIONS[self.id](query, selections)


PREVIEW_COMMAND = (
    "args=$(jq --compact-output --null-input '$ARGS.positional' --args -- %s {q} {+})"
    ' && echo "{\\"function_name\\":\\"%s\\",\\"args\\":$args}" | nc localhost %i'
)

PRESET_PREVIEWS = {
    "basic": "/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/.env/bin/python3.11 -m fzf_primitives.experimental.core.actions.preview_basic {q} {} {+}"
}


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
        preview_command = PRESET_PREVIEWS.get(self.main_preview.id) or self.main_preview.command
        if preview_command is None:
            raise RuntimeError("Preview has no command")
        options = (
            Options()
            .preview(preview_command)
            .add(f"--preview-window={self.main_preview.window_position},{self.main_preview.window_size}")
        )

        # for preview_name, preview in self.previews.items(): # TODO: attach change preview hotkey
        #     options.bind(preview.hotkey, f"execute({RequestCommand(preview_name, socket_number)})")
        return options
