from __future__ import annotations

import time
from threading import Thread
from typing import Callable, Literal

import pyperclip

from ....FzfPrompt import Action, Binding, PromptData
from ....FzfPrompt.action_menu import ParametrizedAction
from ....monitoring import LoggedComponent
from .actions import EntriesGetter, ReloadEntries, SelectBy, ShowInPreview

__all__ = [
    "clip_current_preview",
    "clip_options",
    "FILE_EDITORS",
    "Repeater",
    "FileEditor",
    "ReloadEntries",
    "SelectBy",
    "EntriesGetter",
    "ShowInPreview",
]


# clip current preview
def clip_current_preview(prompt_data: PromptData, converter: Callable[[str], str] | None = None):
    preview_str = prompt_data.get_current_preview()
    if converter:
        preview_str = converter(preview_str)
    pyperclip.copy(preview_str)


# clip options
def clip_options(prompt_data: PromptData):
    pyperclip.copy(str(prompt_data.options))


# open file in editor
type FileEditor = Literal["VS Code", "VS Code - Insiders", "Vi", "Vim", "NeoVim", "Nano"]
FILE_EDITORS: dict[FileEditor, str] = {
    "VS Code": "code",
    "VS Code - Insiders": "code-insiders",
    "Vi": "vi",
    "Vim": "vim",
    "NeoVim": "nvim",
    "Nano": "nano",
}


# repeat actions
class Repeater[T, S]:
    def __init__(
        self,
        *actions: Action,
        repeat_interval: float = 0.5,
        repeat_when: Callable[[PromptData[T, S]], bool] = lambda pd: True,
    ) -> None:
        self.actions = actions
        self.repeat_interval = repeat_interval
        self.repeat_when = repeat_when
        self.thread: AutomatingThread[T, S] | None = None

    def __call__(self, prompt_data: PromptData, FZF_PORT: str):
        prompt_data.server.add_endpoints(Binding("", *self.actions))
        if not self.thread:
            self.thread = self.create_automating_thread(prompt_data, int(FZF_PORT))
            self.thread.start()
        else:
            self.thread.should_stop = True
            self.thread = None

    def create_automating_thread(self, prompt_data: PromptData[T, S], port: int):
        return AutomatingThread(
            prompt_data, port, *self.actions, repeat_interval=self.repeat_interval, repeat_when=self.repeat_when
        )

    def __str__(self) -> str:
        return f"Repeater for {'->'.join(str(action) for action in self.actions)}"


class AutomatingThread[T, S](Thread, LoggedComponent):
    def __init__(
        self,
        prompt_data: PromptData[T, S],
        port: int,
        *actions: Action,
        repeat_interval: float = 0.5,
        repeat_when: Callable[[PromptData[T, S]], bool] = lambda pd: True,
    ) -> None:
        super().__init__(daemon=True)
        LoggedComponent.__init__(self)
        self.is_running = False
        self.should_stop = False
        self.prompt_data = prompt_data
        self.port = port
        self.actions = actions
        self.repeat_interval = repeat_interval
        self.repeat_when = repeat_when

    def run(self) -> None:
        self.prompt_data.controller.execute(
            self.port, Binding("", ParametrizedAction('echo "Auto-updating...$FZF_PROMPT"', "transform-prompt"))
        )
        while True:
            try:
                if not self.repeat_when(self.prompt_data):
                    continue
                self.prompt_data.controller.execute(self.port, Binding("", *self.actions))
            except Exception as err:
                self.logger.exception(err)
                self.should_stop = True
                continue
            finally:
                if self.should_stop:
                    # TODO: reset prompt back to previous
                    self.prompt_data.controller.execute(
                        self.port,
                        Binding("", ParametrizedAction('echo "${FZF_PROMPT#Auto-updating...}"', "transform-prompt")),
                    )
                    break
                time.sleep(self.repeat_interval)
