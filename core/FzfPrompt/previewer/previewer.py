from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from ..server.actions import ServerCall
from .Preview import Preview


class Previewer[T, S](LoggedComponent):
    """Handles storing preview outputs and tracking current preview and possibly other logic associated with previews"""

    def __init__(self) -> None:
        super().__init__()
        self._previews: dict[str, Preview[T, S]] = {}
        self._current_preview: Preview[T, S] | None = None

    @property
    def current_preview(self) -> Preview[T, S]:
        if not self._current_preview:
            raise RuntimeError("No current preview set")
        return self._current_preview

    def set_current_preview(self, preview: Preview[T, S]):
        self._current_preview = preview

    @property
    def previews(self) -> list[Preview[T, S]]:
        return list(self._previews.values())

    def add(self, preview: Preview[T, S], *, main: bool = False):
        self.logger.debug(f"📺 Adding preview '{preview.name}'", trace_point="adding_preview")
        if main or not self._previews:
            self._current_preview = preview
        self._previews[preview.id] = preview

    def resolve_main_preview(self, prompt_data: PromptData):
        if self._current_preview:
            change_preview_output = self._current_preview.change_preview_output
            if isinstance(change_preview_output, ServerCall):
                prompt_data.server.add_endpoint(change_preview_output.endpoint)
            prompt_data.options.preview(change_preview_output.action_value)
            prompt_data.options.add("--preview-window", self._current_preview.change_preview_window.action_value)
            prompt_data.options.preview_label(self._current_preview.change_preview_label.action_value)
