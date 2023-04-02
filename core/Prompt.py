from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Self, Type

from .MyFzfPrompt import Result, run_fzf_prompt
from .options import HOTKEY, Options

if TYPE_CHECKING:
    from .ActionMenu import ActionMenu


# TODO: add support for piping into it
# TODO: add support for processing clipboard
# TODO: add support for running it with custom choices (passed as argument)
# TODO: add support for running it with custom options (passed as argument)
# TODO: add support for accessing attributes of python objects in preview command (using dill?)
# TODO: add support for outputting from all available info (including preview)
class Prompt:
    _options = Options().defaults
    _action_menu_type: Optional[Type[ActionMenu]] = None
    _action_menu_hotkey = HOTKEY.ctrl_y

    def __init__(self, choices: list = None, action_menu: Optional[ActionMenu] = None) -> None:
        self.choices = choices or []
        # Attaching action menu
        self.action_menu = action_menu or self._action_menu_type(self) if self._action_menu_type else None
        if self.action_menu:
            self._options = self._options.expect(self._action_menu_hotkey, *self.action_menu.hotkeyed_actions.keys())

            # HACK: only use singletons
            type(self).__call__ = self.action_menu.wrap(self._action_menu_hotkey)(type(self).__call__)

    # TODO: Replace with .run()?
    def __call__(self, *, options: Options = Options()) -> Result | Self:
        # needs to call run_fzf_prompt(self._options + options)
        return run_fzf_prompt(choices=self.choices, fzf_options=self._options + options)
