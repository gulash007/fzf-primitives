from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Self, Type

if TYPE_CHECKING:
    from .ActionMenu import ActionMenu

from .MyFzfPrompt import Result
from .options import HOTKEY, Options


class Prompt:
    _options = Options().defaults
    _action_menu_type: Optional[Type[ActionMenu]]
    _action_menu_hotkey = HOTKEY.ctrl_y

    def __init__(self) -> None:
        # Attaching action menu
        self.action_menu = None
        if self._action_menu_type:
            self.action_menu = self._action_menu_type(self)
            self._options.expect(self._action_menu_hotkey, *self.action_menu.hotkeyed_actions.keys())

            # HACK: only use singletons
            type(self).__call__ = self.action_menu.wrap(self._action_menu_hotkey)(type(self).__call__)

    def __call__(self) -> Result | Self:
        pass
