import inspect
from typing import Any, Callable, Optional, TypeVar

from thingies import shell_command

from core.exceptions import ExitLoop
from core.MyFzfPrompt import MyFzfPrompt, Result
from core.options import HOTKEY, Options
from core.Prompt import Prompt

PromptType = TypeVar("PromptType", bound=Prompt)


# TODO: Hotkeys class for customizing and checking for hotkey conflicts
def action(hotkey: Optional[str] = None):
    def decorator(func: Callable[[PromptType, str, list[str]], Any]):
        func.is_action = True
        if hotkey:
            func.hotkey = hotkey
        return func

    return decorator


# TODO: return to previous selection
# TODO: return with previous query
# TODO: Allow multiselect (multioutput)?
# TODO: How to include --bind hotkeys (internal fzf prompt actions)? Maybe action menu can just serve as a hotkey hint
class ActionMenu(Prompt):
    _action_menu_type: None = None
    _action_menu_hotkey = None

    def __init__(self, owner: Prompt) -> None:
        super().__init__()
        self.owner = owner
        self.actions = {
            f"{method_name}\t({getattr(method, 'hotkey', '')})": method
            for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if getattr(method, "is_action", None)
        }
        self.hotkeyed_actions = {action.hotkey: action for action in self.actions.values() if hasattr(action, "hotkey")}
        self._options = self._options.expect(*self.hotkeyed_actions.keys())

    def wrap(self, prompt: Prompt):
        prompt_type = type(prompt)
        prompt_call_method = prompt_type.__call__

        def decorator(func):
            def wrapped_prompt_call(slf) -> Result | Prompt:
                result = func(slf)
                if isinstance(result, Prompt):
                    return result
                if result.hotkey == prompt._action_menu_hotkey:
                    # TODO: distinguish between action that returns None and not choosing an action
                    action_menu_result = self(result.query, list(result))
                    return action_menu_result or wrapped_prompt_call(slf)
                if result.hotkey and result.hotkey in self.hotkeyed_actions:
                    return self.interpret_hotkey(result.hotkey, result.query, list(result)) or wrapped_prompt_call(slf)
                return result

            return wrapped_prompt_call

        prompt_type.__call__ = decorator(prompt_call_method)

    def __call__(self, query: str, selections: list[str]) -> Any:
        choices = self.actions.keys()
        result = MyFzfPrompt().prompt(choices, self._options)  # TODO: extract decorated function get_action
        if not result:
            return
        if result.hotkey and result.hotkey != HOTKEY.enter and result.hotkey in self.hotkeyed_actions:
            return self.interpret_hotkey(result.hotkey, query, selections)
        action_id = result[0]
        action = self.actions[action_id]
        return action(query, selections)

    def interpret_hotkey(self, hotkey: str, query: str, selections: list[str]):
        action = self.hotkeyed_actions.get(hotkey)
        return action(query, selections) if action else None

    # EXAMPLE
    @action(HOTKEY.ctrl_c)
    def clip_selections(self, query: str, selections: list[str]):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        shell_command("clip", input="\n".join(selections))

    @action(HOTKEY.ctrl_q)
    def quit_app(self, query: str, selections: list[str]):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        raise ExitLoop(f"Exiting from {self} with query: {query} and selections: {', '.join(selections)}")


if __name__ == "__main__":

    class SomePrompt(Prompt):
        _action_menu_type = ActionMenu

        def __call__(self) -> Any:
            return self.get_number()

        @Options().multiselect
        def get_number(self, options: Options = Options()):
            return MyFzfPrompt().prompt(["alpha", "beta", "gamma"], self._options + options)

    pr = SomePrompt()
    print(pr())
