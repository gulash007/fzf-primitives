from pathlib import Path
from typing import Callable, Iterable

from ..config import Config
from .FzfPrompt import Binding, PromptData, Result, ServerCall, execute_fzf
from .FzfPrompt.decorators import single_use_method
from .mods import Mod


class Prompt[T, S]:
    config = Config

    def __init__(
        self,
        entries: list[T] | None = None,
        converter: Callable[[T], str] = str,
        obj: S = None,
        *,
        entries_stream: Iterable[T] | None = None,
        use_basic_hotkeys: bool | None = None,
    ):
        self._entries_stream = entries_stream
        self._converter = converter
        self._prompt_data = PromptData(entries=entries, converter=converter, obj=obj)
        self._mod = Mod()
        if use_basic_hotkeys is None:
            use_basic_hotkeys = Config.use_basic_hotkeys
        if use_basic_hotkeys:
            self._mod.on_hotkey(Config.default_accept_hotkey).accept()
            self._mod.on_hotkey(Config.default_abort_hotkey).abort()

    @property
    def mod(self) -> Mod[T, S]:
        return self._mod

    @property
    def entries(self) -> list[T]:
        return self._prompt_data.entries

    @property
    def obj(self) -> S:
        return self._prompt_data.obj

    @property
    def current_preview(self):
        return self._prompt_data.get_current_preview()

    @single_use_method
    def run(self, executable_path: str | Path | None = None) -> Result[T, S]:
        self._run_initial_setup()
        return execute_fzf(self._prompt_data, executable_path=executable_path, entries_stream=self._entries_stream)

    @single_use_method
    def _run_initial_setup(self):
        self.mod.apply(self._prompt_data)
        if self._entries_stream is not None:
            # Ensure that the preview is refreshed with new lines
            self._prompt_data.action_menu.add(
                "result", Binding("refresh preview", "refresh-preview"), on_conflict="append"
            )

        self._prompt_data.previewer.resolve_main_preview(self._prompt_data)
        if self._prompt_data.should_run_automator:
            self._prompt_data.automator.prepare()
            self._prompt_data.automator.start()

        def on_startup_success(prompt_data: PromptData, FZF_PORT: str):
            self._prompt_data.set_stage("running")
            if FZF_PORT.isdigit():
                self._prompt_data.control_port = int(FZF_PORT)

        self._prompt_data.action_menu.add(
            "start",
            Binding("On startup success", ServerCall(on_startup_success, command_type="execute-silent")),
            on_conflict="prepend",
        )
        for trigger, binding in self._prompt_data.action_menu.bindings.items():
            self._prompt_data.server.add_endpoints(binding, trigger)
        self._prompt_data.options += self._prompt_data.action_menu.resolve_options()
        self._prompt_data.options.listen()  # for ServerCalls with FZF_PORT parameter
        self._stage = "ready to run"
