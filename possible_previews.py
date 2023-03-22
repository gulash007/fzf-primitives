from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Callable, Self

from pyfzf import FzfPrompt
from thingies import SortingKey

from core.exceptions import ExitLoop
from core.options import Options

# class HOTKEY(Enum):
#     ctrl_q = "ctrl-q"
#     ctrl_a = "ctrl-a"
#     ctrl_c = "ctrl-c"
#     esc = "esc"

#     def __call__(self, func: Callable):
#         owner_of_func = get_owner(func)

#         # owner_of_func._options =
#         def with_hotkey(slf, *args, **kwargs):
#             return

#         return with_hotkey


# class Prompt:
#     # Hotkey interpretation needs to happen inside prompt. It should output either a selection or a list of selections
#     # ? Transformation of selection or of all lines should be a part of prompt ?

#     def __post_init__(self):
#         # Setup options here
#         # Should options be parametrized somehow after creation of Prompt object? Or should they be parametrized only by creation?
#         ## Yeah, only at creation, so all here or in definition
#         self._action_menu: ActionMenu = ActionMenu()
#         _preview: Preview = Preview()
#         self._options: Options = Options().preview(_preview)

#     @Options().bind(HOTKEY.ctrl_c.value, lambda self: self.action_menu())
#     def __call__(self) -> Result:
#         """Runs prompt"""
#         return Result(FzfPrompt().prompt(choices=self._get_choices(), fzf_options=str(self._options)))

#     def _get_choices(self):
#         return [1, 2, 3]

#     def quit(self):
#         raise ExitLoop


# class ActionMenu(Prompt):
#     """Is also a prompt but has no action menu itself"""

#     action_menu: None = None

#     def attach_to(self, owner: Prompt):
#         self._owner = owner

#     @HOTKEY.esc
#     def go_back_to_owner(self):  # TODO
#         """Go back to prompt that invoked it"""
#         self._owner()


# class Preview:
#     def __init__(self) -> None:
#         self._command: Callable | str


class Result:
    """Expects at least one --expect=hotkey so that it can interpret the first element in fzf_result as hotkey"""

    def __init__(self, fzf_result: list[str]) -> None:
        self.hotkey = fzf_result[0]
        self.values = fzf_result[1:]

    def consume(self, hotkey: str):
        if self.hotkey == hotkey:
            self.hotkey = None
            return True
        return False

    def __str__(self) -> str:
        return json.dumps(self.__dict__)


REPO_LOCATION = Path("/Users/honza/Documents/HOLLY")


class ObsidianBrowser:
    def run(self):
        prompt = DirectoryPrompt(REPO_LOCATION)
        while True:
            try:
                result = prompt()
                if not isinstance(result, DirectoryPrompt):
                    return result
                prompt = result
                continue
            except ExitLoop:
                break


class DirectoryPrompt:
    def __init__(self, dirpath: Path, sorting_key: Callable = SortingKey().alphabetically) -> None:
        self.dirpath = dirpath
        self._options = Options().defaults.ansi
        self._sorting_key = sorting_key

    def __call__(self):
        files = sorted(self.dirpath.iterdir(), key=self._sorting_key)
        return Result(FzfPrompt().prompt(choices=files, fzf_options=str(self._options)))


ob = ObsidianBrowser()

print(ob.run())
