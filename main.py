from typing import Callable

from .core.FzfPrompt.Prompt import PromptData, Result, run_fzf_prompt
from .core.mods import Mod


# TODO: choose preset prompt mods in constructor ("default" by default, "base" will return an unmodded prompt)
# TODO: Or choose the presets in Mod class as its properties
# TODO: Maybe replace presenter with displayed_choices ❌ but then you have to make sure their length matches
class Prompt[T, S]:
    def __init__(self, choices: list[T] | None = None, presenter: Callable[[T], str] = str, obj: S = None):
        self._prompt_data = PromptData(choices=choices, presenter=presenter, obj=obj)
        self._mod = Mod(self._prompt_data)  # TODO: prevent from using after run

    @property
    def mod(self) -> Mod:
        return self._mod

    # TODO: should this return immutable sequence? But then you can't adjust them before running unless you want to use a condition to check if prompt is already running
    @property
    def choices(self) -> list[T]:
        return self._prompt_data.choices

    @property
    def obj(self) -> S:
        return self._prompt_data.obj

    @property
    def current_preview(self):
        return self._prompt_data.get_current_preview()

    def run(self) -> Result[T]:
        self.mod.apply_options()
        return run_fzf_prompt(self._prompt_data)
