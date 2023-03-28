import inspect
from typing import Any, Callable, Optional
from core.MyFzfPrompt import Result, MyFzfPrompt
from possible_previews import Prompt
from typing import TypeVar
from thingies import shell_command

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
class ActionMenu(Prompt):
    def __init__(self, owner: Prompt, query: str, selections: list[str]) -> None:
        self.owner = owner
        self.query = query
        self.selections = selections
        self.actions = {
            method_name: method
            for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if getattr(method, "is_action", None)
        }
        self.hotkeyed_actions = {action.hotkey: action for action in self.actions.values() if hasattr(action, "hotkey")}
        super().__init__()

    def __call__(self) -> Result:
        choices = self.actions.keys()
        action_name = MyFzfPrompt().prompt(choices=choices)[0]  # TODO: extract decorated function
        return self.actions[action_name](self.query, self.selections)

    def interpret_hotkey(self, hotkey: str):
        return self.hotkeyed_actions[hotkey](self.query, self.selections)

    @action("ctrl-c")
    def clip_selections(self, query: str, selections: list[str]):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        shell_command("clip", input="\n".join(selections))


if __name__ == "__main__":
    am = ActionMenu(None, "some query", ["selection1", "selection2"])
    am()
