from .core.FzfPrompt.constants import DEFAULT_ACCEPT_HOTKEY, DEFAULT_ABORT_HOTKEY
from .core.FzfPrompt.Prompt import PromptData, Result, run_fzf_prompt
from .core.mods import Mod


# TODO: choose preset prompt mods in constructor ("default" by default, "base" will return an unmodded prompt)
# TODO: Or choose the presets in Mod class as its properties
# TODO: Maybe replace presenter with displayed_choices ❌ but then you have to make sure their length matches
class Prompt[T, S]:
    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        *,
        override_basic_hotkeys: bool = False,
    ):
        self._prompt_data = PromptData(choices=choices, presented_choices=presented_choices, obj=obj)
        self._mod = Mod(self._prompt_data)  # TODO: prevent from using after run
        if not override_basic_hotkeys:
            self._mod.on_event(DEFAULT_ACCEPT_HOTKEY).accept
            self._mod.on_event(DEFAULT_ABORT_HOTKEY).abort

    @property
    def mod(self) -> Mod[T, S]:
        return self._mod

    # TODO: should this return immutable sequence? But then you can't adjust them before running unless you want to use a condition to check if prompt is already running
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

    def run(self) -> Result[T]:
        # FIXME: only mod.options modifications are applied this late; all other mods are applied immediately
        self.mod.apply_options()
        return run_fzf_prompt(self._prompt_data)
