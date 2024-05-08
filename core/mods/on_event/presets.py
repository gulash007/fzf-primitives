from __future__ import annotations

import shlex
import subprocess
from threading import Thread
from typing import Literal

import pyperclip

from fzf_primitives.core.monitoring import LoggedComponent

from ...FzfPrompt import Action, Binding, PromptData


def clip_current_preview(prompt_data: PromptData):
    pyperclip.copy(prompt_data.get_current_preview())


def clip_options(prompt_data: PromptData):
    pyperclip.copy(str(prompt_data.options))


type FileEditor = Literal["VS Code", "VS Code - Insiders", "Vi", "Vim", "NeoVim", "Nano"]
FILE_EDITORS: dict[FileEditor, str] = {
    "VS Code": "code",
    "VS Code - Insiders": "code-insiders",
    "Vi": "vi",
    "Vim": "vim",
    "NeoVim": "nvim",
    "Nano": "nano",
}


class Repeater:
    def __init__(self, *actions: Action, repeat_interval: float = 0.5) -> None:
        self.actions = actions
        self.repeat_interval = repeat_interval
        self.thread = self.create_automating_thread()

    def __call__(self, prompt_data: PromptData, FZF_PORT: str):
        prompt_data.action_menu.add_server_calls(Binding("", *self.actions))
        self.thread.set_port(FZF_PORT)
        if not self.thread.is_running:
            subprocess.Popen(
                shlex.join(["curl", "-XPOST", f"localhost:{FZF_PORT}", "-d", "change-prompt(Auto-updating...> )"]),
                shell=True,
            )
            self.thread.start()
            self.thread.is_running = True
        else:
            # TODO: reset prompt back to previous
            subprocess.Popen(
                shlex.join(["curl", "-XPOST", f"localhost:{FZF_PORT}", "-d", "change-prompt(> )"]),
                shell=True,
            )
            self.thread.should_stop = True
            self.thread = self.create_automating_thread()

    def create_automating_thread(self):
        return AutomatingThread(*self.actions, repeat_interval=self.repeat_interval)


class AutomatingThread(Thread, LoggedComponent):
    def __init__(self, *actions: Action, repeat_interval: float = 0.5) -> None:
        super().__init__(daemon=True)
        LoggedComponent.__init__(self)
        self.is_running = False
        self.should_stop = False
        self.actions = actions
        self.repeat_interval = repeat_interval
        self.port: str

    def run(self) -> None:
        import subprocess
        import time

        while True:
            try:
                subprocess.Popen(
                    shlex.join(
                        [
                            "curl",
                            "-XPOST",
                            f"localhost:{self.port}",
                            "-d",
                            Binding("", *self.actions).to_action_string(),
                        ]
                    ),
                    shell=True,  # ❗ required for getting FZF_PORT
                )
                if self.should_stop:
                    break
            except Exception as err:
                self.logger.exception(err)
                continue
            finally:
                time.sleep(self.repeat_interval)

    def set_port(self, port: str):
        self.port = port
