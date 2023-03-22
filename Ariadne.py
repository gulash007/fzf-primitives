from __future__ import annotations
from typing import Optional
from core import mods
from thingies import shell_command
from pyfzf import FzfPrompt
from core.exceptions import ExitLoop, ExitRound

# WORKSPACE NAVIGATOR

# TODO: Use https://github.com/fgmacedo/python-statemachine
# TODO: Programmatic choices


class State:
    """Represents position in the Ariadne FSM"""

    # TODO: string as position (how can position-as-string maintain backwards compatibility?)
    def __init__(self, string: Optional[str] = None) -> None:
        # position-defining attributes
        pass


class Ariadne:
    def __init__(self, starting_position: Optional[State] = State()) -> None:
        self.starting_position = starting_position
        self.position = starting_position

    def run(self):
        prompt = FzfPrompt()
        choice = prompt.prompt(choices=self.get_choices())
        self.position = self.change_position(choice)
        shell_command("open raycast://extensions/raycast/raycast/confetti")

    def run_in_loop(self):
        while True:
            try:
                self.run()
            except ExitRound:
                continue
            except ExitLoop:
                print("Exiting loop")
                return

    def change_position(self, choice) -> State:
        return State()

    def get_choices(self) -> list[str]:
        return []


if __name__ == "__main__":
    a = Ariadne()
    a.run_in_loop()
