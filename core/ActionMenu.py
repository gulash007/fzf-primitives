from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Optional, ParamSpec, TypeVar

from thingies import shell_command

from .exceptions import ExitLoop
from .MyFzfPrompt import Result, run_fzf_prompt
from .options import HOTKEY, Options
from .Prompt import Prompt

P = ParamSpec("P")
R = TypeVar("R")


# TODO: Hotkeys class for customizing and checking for hotkey conflicts
def action(hotkey: Optional[str] = None):
    def decorator(func: Callable[[ActionMenu, Result], Any]):
        func.is_action = True
        if hotkey:
            func.hotkey = hotkey
        return func

    return decorator


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
        self.prompt: Prompt

    def attach(self, prompt: Prompt):
        """In case actions being parametrized with attributes of prompt"""
        self.prompt = prompt

    # TODO: type hints
    def __call__(self, func: Callable[P, Result | Prompt]) -> Callable[P, Result | Prompt]:
        @functools.wraps(func)
        def wrapped_prompt_call(*args: P.args, **kwargs: P.kwargs) -> Result | Prompt:
            options = kwargs.get("options", Options())
            if not isinstance(options, Options):
                raise TypeError(f"options kw bad type: {type(options)}: {options}")
            options = options.expect(self._hotkey, *self.hotkeyed_actions.keys())
            options = options.header(f"tip: Invoke action menu with {self._hotkey}")
            options = options.header_first
            kwargs["options"] = options
            result = func(*args, **kwargs)
            if isinstance(result, Prompt):
                return result
            if result.hotkey == self._hotkey:
                # TODO: distinguish between action that returns None and not choosing an action
                return self.run(result) or wrapped_prompt_call(*args, **kwargs)
            if result.hotkey and result.hotkey in self.hotkeyed_actions:
                return self.hotkeyed_actions[result.hotkey](result) or wrapped_prompt_call(*args, **kwargs)
            return result

        return wrapped_prompt_call

    def run(self, result: Result) -> Any:
        choices = self.actions.keys()
        action_selection = run_fzf_prompt(choices, self._options)  # TODO: extract decorated function get_action
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

    # EXAMPLE
    @action(HOTKEY.enter)
    def select(self, result: Result):
        return result

    @action(HOTKEY.ctrl_c)
    def clip_selections(self, result: Result):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        shell_command("clip", input="\n".join(result))

    @action(HOTKEY.ctrl_q)
    def quit_app(self, result: Result):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        raise ExitLoop(f"Exiting from {self} with\n\tquery: {result.query}\n\tselections: {', '.join(result)}")


if __name__ == "__main__":
    action_menu = ActionMenu()

    @Options().multiselect
    @action_menu
    def some_prompt(options: Options = Options()):
        return run_fzf_prompt(choices=[1, 2, 3], options=options)

    print(some_prompt())
