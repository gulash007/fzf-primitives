from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from .options import Hotkey, Options
from .Previewer import Preview

if TYPE_CHECKING:
    from .Prompt import Result
    from ..mods import Moddable, P
    from .PromptData import PromptData

# TODO: ❗ hotkey conflicts
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
    command: str
    hotkey: Hotkey

    @classmethod
    def change_preview(cls, preview: Preview) -> Self:
        return cls(
            f"Change preview to '{preview.id}'",
            f"change-preview({preview.command})+change-preview-window({preview.window_size},{preview.window_position})+refresh-preview",
            preview.hotkey,
        )

    def __call__(self, func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.add_action(self)
            return func(prompt_data, *args, **kwargs)

        return with_preview


class ActionMenu:
    def __init__(self) -> None:
        self._options = Options()
        self.actions: list[Action] = []

    def add(self, action: Action):
        self.actions.append(action)
        self._options.bind(action.hotkey, action.command)

    def resolve_options(self) -> Options:
        header_help = "\n".join(f"{action.hotkey}\t{action.name}" for action in self.actions)
        return self._options.header(header_help).header_first

    def process_result(self, result: Result):
        return result
