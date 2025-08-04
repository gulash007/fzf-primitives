from pathlib import Path
from typing import Callable, Iterable

from ..config import Config
from .FzfPrompt import PromptData, Result, run_fzf_prompt
from .FzfPrompt.decorators import single_use_method
from .mods import Mod


class Prompt[T, S]:
    config = Config

    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        *,
        use_basic_hotkeys: bool | None = None,
    ):
        self._prompt_data = PromptData(choices=choices, presented_choices=presented_choices, obj=obj)
        self._mod = Mod()
        if use_basic_hotkeys is None:
            use_basic_hotkeys = Config.use_basic_hotkeys
        if use_basic_hotkeys:
            self._mod.on_hotkey(Config.default_accept_hotkey).accept
            self._mod.on_hotkey(Config.default_abort_hotkey).abort

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

    # FIXME: Merge run and run_with_stream into one method so that only one can be used
    @single_use_method
    def run(self, executable_path: str | Path | None = None) -> Result[T]:
        self.mod.apply(self._prompt_data)
        return run_fzf_prompt(self._prompt_data, executable_path=executable_path)

    @single_use_method
    def run_with_stream(
        self, readable: Iterable[T], convertor: Callable[[T], str], executable_path: str | Path | None = None
    ) -> Result[T]:
        # Ensure that the preview is refreshed with new lines
        self.mod.on_situation(on_conflict="append").RESULT.refresh_preview
        self.mod.apply(self._prompt_data)
        return run_fzf_prompt(
            self._prompt_data,
            readable=readable,
            convertor=convertor,
            executable_path=executable_path,
        )
