from pathlib import Path

from .. import config
from .FzfPrompt import PromptData, Result, run_fzf_prompt
from .FzfPrompt.decorators import single_use_method
from .mods import Mod


# TODO: Presented choices should have the same length as choices
# TODO: Add choice of logging level
class Prompt[T, S]:
    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        *,
        use_basic_hotkeys: bool | None = None,
    ):
        self._prompt_data = PromptData(choices=choices, presented_choices=presented_choices, obj=obj)
        self._mod = Mod(self._prompt_data)  # TODO: prevent from using after run
        if use_basic_hotkeys is None:
            use_basic_hotkeys = config.USE_BASIC_HOTKEYS
        if use_basic_hotkeys:
            self._mod.on_hotkey(config.DEFAULT_ACCEPT_HOTKEY).accept
            self._mod.on_hotkey(config.DEFAULT_ABORT_HOTKEY).abort

    @property
    def mod(self) -> Mod[T, S]:
        return self._mod

    @property
    def choices(self) -> list[T]:
        return self._prompt_data.choices

    @property
    def presented_choices(self) -> list[str]:
        return self._prompt_data.presented_choices

    @property
    def obj(self) -> S:
        return self._prompt_data.obj

    @property
    def current_preview(self):
        return self._prompt_data.get_current_preview()

    @single_use_method
    def run(self, executable_path: str | Path | None = None) -> Result[T]:
        self.mod.apply()
        return run_fzf_prompt(self._prompt_data, executable_path=executable_path)
