import inspect
from typing import Any, Callable, Optional, TypeVar
from .BasicLoop import BasicLoop

from thingies import shell_command

from .BasicLoop import BasicRecursiveLoop
from .exceptions import ExitLoop
from .MyFzfPrompt import run_fzf_prompt, Result
from .options import HOTKEY, Options
from .Prompt import Prompt

PromptType = TypeVar("PromptType", bound=Prompt)


# TODO: Hotkeys class for customizing and checking for hotkey conflicts
def action(hotkey: Optional[str] = None):
    def decorator(func: Callable[[PromptType, Result], Any]):
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
class ActionMenu(Prompt):
    _action_menu_type: None = None
    _action_menu_hotkey = None

    def __init__(self, owner: Optional[Prompt] = None) -> None:
        super().__init__()
        self.owner = owner
        self.actions: dict[str, Callable[[Result], Any]] = {
            f"{method_name}\t({getattr(method, 'hotkey', '')})": method
            for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if getattr(method, "is_action", None)
        }
        self.hotkeyed_actions = {action.hotkey: action for action in self.actions.values() if hasattr(action, "hotkey")}
        self._options = self._options.expect(*self.hotkeyed_actions.keys())
        self._options = self._options.header("tip: Press esc to go back")
        self._options = self._options.header_first

    def wrap(self, action_menu_hotkey: str = HOTKEY.ctrl_y):
        def decorator(func: Callable):
            def wrapped_prompt_call(*args, **kwargs) -> Result | Prompt:
                result = func(*args, **kwargs)
                if isinstance(result, Prompt):
                    return result
                if result.hotkey == action_menu_hotkey:
                    # TODO: distinguish between action that returns None and not choosing an action
                    return self(result) or wrapped_prompt_call(*args, **kwargs)
                if result.hotkey and result.hotkey in self.hotkeyed_actions:
                    return self._interpret_hotkey(result) or wrapped_prompt_call(*args, **kwargs)
                return result

            return wrapped_prompt_call

        return decorator

    def __call__(self, result: Result) -> Any:
        choices = self.actions.keys()
        action_selection = run_fzf_prompt(choices, self._options)  # TODO: extract decorated function get_action
        if not action_selection:
            return
        if (
            action_selection.hotkey
            and action_selection.hotkey != HOTKEY.enter
            and action_selection.hotkey in self.hotkeyed_actions
        ):
            return self._interpret_hotkey(result)
        action_id = action_selection[0]
        action = self.actions[action_id]
        return action(result)

    def _interpret_hotkey(self, result: Result):
        action = self.hotkeyed_actions.get(result.hotkey)
        return action(result) if action else None

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
        raise ExitLoop(f"Exiting from {self} with query: {result.query} and selections: {', '.join(result)}")


if __name__ == "__main__":
    # class SomePrompt(Prompt):
    #     _action_menu_type = ActionMenu
    #     action_menu: ActionMenu

    #     def __call__(self) -> Any:
    #         result = self.get_number()
    #         if result.hotkey == HOTKEY.enter:
    #             if "🔄" not in result:
    #                 self.action_menu.clip_selections(result)
    #             return self
    #         return result

    #     @Options().multiselect
    #     def get_number(self, options: Options = Options()):
    #         return run_fzf_prompt(["alpha", "beta", "gamma", "🔄"], self._options + options)

    # # pr = SomePrompt()
    # # print(pr())
    # bl = BasicRecursiveLoop(SomePrompt())
    # print(bl.run())
    am = ActionMenu()

    # TODO: automatically pass hotkeys to --expect option
    @am.wrap(HOTKEY.ctrl_y)
    def some_prompt():
        return run_fzf_prompt([1, 2, 3], fzf_options=Options().expect(*am.hotkeyed_actions.keys()))

    some_prompt()
