from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
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
        self.logger.debug(f"📺 Adding preview '{preview.name}'")
        if main or not self._previews:
            self._current_preview = preview
        self._previews[preview.id] = preview

    def resolve_main_preview(self, prompt_data: PromptData):
        if self._current_preview:
            prompt_data.add_binding("start", self._current_preview.preview_change_binding, on_conflict="prepend")
