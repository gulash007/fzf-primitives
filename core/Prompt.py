from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Self, Type

if TYPE_CHECKING:
    from core.ActionMenu import ActionMenu

from core.MyFzfPrompt import Result
from core.options import HOTKEY, Options


class Prompt:
    _options = Options().defaults
    _action_menu_type: Optional[Type[ActionMenu]]
    _action_menu_hotkey = HOTKEY.ctrl_y

    def __init__(self) -> None:
        # Attaching action menu
        self.action_menu = None
        if self._action_menu_type:
            self.action_menu = self._action_menu_type(self)
            self._options = self._options.expect(self._action_menu_hotkey, *self.action_menu.hotkeyed_actions.keys())
            # self.action_menu.wrap(self)
            self.action_menu.wrap(self)

    def __call__(self) -> Result | Self:
        pass
