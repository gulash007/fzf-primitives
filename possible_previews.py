from __future__ import annotations

from pathlib import Path
from typing import Callable
from core import mods

from thingies import SortingKey, shell_command

from core.MyFzfPrompt import Result, run_fzf_prompt
from core.options import HOTKEY, Options

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


REPO_LOCATION = Path("/Users/honza/Documents/HOLLY")


class UnexpectedResultType(Exception):
    pass


class BasicLoop:
    def __init__(self, starting_prompt: Prompt) -> None:
        self.starting_prompt = starting_prompt

    def run(self) -> Result:
        prompt = self.starting_prompt
        while True:
            result = prompt()
            if isinstance(result, Result):
                return result
            elif isinstance(result, Prompt):
                prompt = result
                continue
            else:
                raise UnexpectedResultType(f"{type(result)}")


class Prompt:
    def __init__(self) -> None:
        self._options = Options().defaults

    def __call__(self) -> Result:
        pass


class DirectoryPrompt(Prompt):
    def __init__(self, dirpath: Path, sorting_key: Callable = SortingKey().alphabetically) -> None:
        super().__init__()
        self.dirpath = dirpath
        self._sorting_key = sorting_key

    @mods.hotkey_python(HOTKEY.ctrl_d, lambda self, result: self.double_query(result))
    @Options().ansi.multiselect
    def __call__(self, options: Options = Options()) -> Result:
        files = sorted(
            (Path(line) for line in shell_command(f"find {self.dirpath} -maxdepth 1").splitlines()),
            key=self._sorting_key,
        )
        return run_fzf_prompt(choices=files, fzf_options=self._options + options)


if __name__ == "__main__":
    d = DirectoryPrompt(REPO_LOCATION, sorting_key=SortingKey().directory_first().alphabetically())
    basic_loop = BasicLoop(d)

    print(basic_loop.run())
