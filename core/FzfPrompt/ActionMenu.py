from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from .options import Hotkey, Options
from .Previewer import Preview

if TYPE_CHECKING:
    from .Prompt import Result

# TODO: Hotkeys class for customizing and checking for hotkey conflicts
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Allow multiselect (multioutput)?
# TODO: How to include --bind hotkeys (internal fzf prompt actions)? Maybe action menu can just serve as a hotkey hint
# Decorator to turn a function into a script that is then used with --bind 'hotkey:execute(python script/path {q} {+})'
# TODO: enter action in ActionMenu
# TODO: hotkeys only in ActionMenu prompt (not consumed in owner prompt)
# TODO: Instead of interpreting falsey values as reset, there should be an explicit named exception raised and caught
# TODO: Sort actions
# TODO: Show action menu as preview (to see hotkeys without restarting prompt)
# TODO: Make action_menu_hotkey owned by ActionMenu instead of prompt
# TODO: Will subclasses need more than just define actions? Maybe some more options can be overridden?
# TODO: Preview of result
# TODO: ❗ Remake as an hotkey:execute(action_menu_prompt <prompt id (port #)>)
# TODO: - How to invoke it through --bind and recreate the action back in the owner prompt?


@dataclass
class Action:
    name: str
    hotkey: Hotkey
    command: str

    @classmethod
    def change_preview(cls, preview: Preview) -> Self:
        assert preview.command
        return cls(
            f"Change preview to '{preview.id}'",
            preview.hotkey,
            f"change-preview({preview.command})+change-preview-window({preview.window_size},{preview.window_position})",
        )
        # FIXME: changing preview doesn't update preview output immediately


class ActionMenu:
    def __init__(self, hotkey: Hotkey = "ctrl-h") -> None:
        # self.hotkey_manager: HotkeyManager # TODO
        # self.action: dict[str, Action] # TODO: class Action?
        self._hotkey: Hotkey = hotkey
        self.actions: list[Action] = []
        self._options = Options().header(f"tip: Invoke action menu with {self._hotkey}").header_first
        # TODO: add hotkey to run action menu or just show hotkeys as preview

    def add(self, action: Action):
        self.actions.append(action)
        self._options.bind(action.hotkey, action.command)

    def resolve_options(self) -> Options:
        return self._options

    def process_result(self, result: Result):
        return result

    # TODO
    def as_preview(self) -> Preview:
        return Preview()
