from thingies import shell_command

from .ActionMenu import ActionMenu, as_action
from .exceptions import ExitLoop
from .MyFzfPrompt import Result
from .options import HOTKEY


class DefaultActionMenu(ActionMenu):
    @as_action(HOTKEY.enter)
    def select(self, result: Result):
        return result

    @as_action(HOTKEY.ctrl_c)
    def clip_selections(self, result: Result):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        shell_command("clip", input="\n".join(result))

    @as_action(HOTKEY.ctrl_q)
    def quit_app(self, result: Result):
        # shell_command seems faster than pyperclip but not in a loop but that's probably irrelevant
        raise ExitLoop(f"Exiting from {self} with\n\tquery: {result.query}\n\tselections: {', '.join(result)}")
