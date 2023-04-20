from thingies import shell_command

from .ActionMenu import ActionMenu, action
from .exceptions import ExitLoop
from .FzfPrompt.Prompt import Result
from .FzfPrompt.options import HOTKEY


class DefaultActionMenu(ActionMenu):
    @action("enter")
    def select(self, result: Result):
        return result

    @action("ctrl-c")
    def clip_selections(self, result: Result):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        shell_command("clip", input_="\n".join(result))

    @action("ctrl-q")
    def quit_app(self, result: Result):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        sep = "\n\t"
        raise ExitLoop(f"Exiting from {self} with\nquery: {result.query}\nselections:{sep}{sep.join(result)}")
