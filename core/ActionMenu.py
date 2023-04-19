from __future__ import annotations

import inspect
from typing import Any, Callable, TypeVar

from ..core.intercom.PromptData import PromptData

from ..core import mods
from . import Prompt
from .helpers.type_hints import Moddable, P
from .MyFzfPrompt import Result, run_fzf_prompt
from .options import HOTKEY, Options


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
class ActionMenu:
    def __init__(self, hotkey: str = HOTKEY.ctrl_h) -> None:
        self._hotkey = hotkey
        self.actions: dict[str, Callable[[Result], Any]] = {
            f"{method_name}\t({getattr(method, 'hotkey', '')})": method
            for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if getattr(method, "is_action", None)
        }
        self.hotkeyed_actions = {action.hotkey: action for action in self.actions.values() if hasattr(action, "hotkey")}
        self._options = Options().expect(*self.hotkeyed_actions.keys())
        self._options = self._options.header("tip: Press esc to go back")
        self._options = self._options.header_first

    def __call__(self, func: Moddable[P]) -> Moddable[P]:
        def wrapped_prompt_run(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = prompt_data.options.expect(self._hotkey, *self.hotkeyed_actions.keys())
            prompt_data.options = prompt_data.options.header(f"tip: Invoke action menu with {self._hotkey}")
            prompt_data.options = prompt_data.options.header_first
            result = func(prompt_data, *args, **kwargs)
            if result.hotkey == self._hotkey:
                # TODO: distinguish between action that returns None and not choosing an action
                return self.run(result) or wrapped_prompt_run(prompt_data, *args, **kwargs)
            if result.hotkey and result.hotkey in self.hotkeyed_actions:
                return self.hotkeyed_actions[result.hotkey](result) or wrapped_prompt_run(prompt_data, *args, **kwargs)
            return result

        return wrapped_prompt_run

    def run(self, result: Result) -> Any:
        choices = list(self.actions.keys())
        action_selection = run_fzf_prompt(
            PromptData(choices=choices, options=self._options)
        )  # TODO: extract decorated function get_action
        if not action_selection and not action_selection.hotkey:
            return
        if (
            action_selection.hotkey
            and action_selection.hotkey != HOTKEY.enter
            and action_selection.hotkey in self.hotkeyed_actions
        ):
            return self.hotkeyed_actions[action_selection.hotkey](result)
        action_id = action_selection[0]
        return self.actions[action_id](result)


AnyActionMenu = TypeVar("AnyActionMenu", bound=ActionMenu)


def action(hotkey: str | None = None):
    def decorator(func: Callable[[AnyActionMenu, Result], Any]):
        func.is_action = True
        if hotkey:
            func.hotkey = hotkey
        return func

    return decorator


if __name__ == "__main__":
    action_menu = ActionMenu()

    @mods.add_options(Options().multiselect)
    @mods.add_options(Options("--bind 'change:execute-silent(nc localhost 34566)'"))
    @action_menu
    def some_prompt(prompt_data: PromptData):
        return Prompt.run(prompt_data)

    print(some_prompt(PromptData(choices=[1, 2, 3])))
