from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..prompt_data import PromptData
from ...monitoring import LoggedComponent
from .Preview import Preview
from ..action_menu import ActionMenu, ConflictResolution
from ..options import Hotkey, Situation


class Previewer[T, S](LoggedComponent):
    """Handles storing preview outputs and tracking current preview and possibly other logic associated with previews"""

    def __init__(self, action_menu: ActionMenu) -> None:
        super().__init__()
        self._previews: dict[str, Preview[T, S]] = {}
        self._current_preview: Preview[T, S] | None = None
        self._action_menu = action_menu

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

    def add(
        self,
        preview: Preview[T, S],
        event: Hotkey | Situation | None = None,
        *,
        conflict_resolution: ConflictResolution = "raise error",
        main: bool = False,
    ):
        self.logger.debug(f"📺 Adding preview '{preview.name}'")
        if main or not self._previews:
            self._current_preview = preview
        self._previews[preview.id] = preview
        if event:
            self._action_menu.add(event, preview.preview_change_binding, conflict_resolution=conflict_resolution)
        else:
            self._action_menu.add_server_calls(preview.preview_change_binding)

    def resolve_main_preview(self, prompt_data: PromptData[T, S]):
        if self._current_preview:
            self._action_menu.add("start", self._current_preview.preview_change_binding, conflict_resolution="prepend")
