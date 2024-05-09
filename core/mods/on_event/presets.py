from __future__ import annotations

import shlex
import subprocess
import time
from threading import Thread
from typing import Callable, Literal

import pyperclip

from ...FzfPrompt import Action, Binding, ChoicesAndLinesMismatch, PromptData, ServerCall
from ...monitoring import LoggedComponent


# clip current preview
def clip_current_preview(prompt_data: PromptData):
    pyperclip.copy(prompt_data.get_current_preview())


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

# reload choices
type ChoicesGetter[T, S] = Callable[[PromptData[T, S]], tuple[list[T], list[str] | None]]


class ReloadChoices[T, S](ServerCall[T, S]):
    def __init__(self, choices_getter: ChoicesGetter[T, S], *, sync: bool = False):
        def reload_choices(prompt_data: PromptData[T, S]):
            choices, lines = choices_getter(prompt_data)
            if lines is None:
                lines = [str(choice) for choice in choices]
            else:
                try:
                    prompt_data.check_choices_and_lines_length(choices, lines)
                except ChoicesAndLinesMismatch as err:
                    input(str(err))
                    raise
            prompt_data.choices = choices
            prompt_data.presented_choices = lines
            return "\n".join(lines)

        super().__init__(reload_choices, command_type="reload-sync" if sync else "reload")

    def __str__(self) -> str:
        return f"[RC]({self.function.__name__})"


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
        prompt_data.server.add_server_calls(Binding("", *self.actions))
        if not self.thread:
            self.thread = self.create_automating_thread(prompt_data, FZF_PORT)
            self.thread.start()
        else:
            self.thread.should_stop = True
            self.thread = None

    def create_automating_thread(self, prompt_data: PromptData[T, S], port: str):
        return AutomatingThread(
            prompt_data, port, *self.actions, repeat_interval=self.repeat_interval, repeat_when=self.repeat_when
        )

    def __str__(self) -> str:
        return f"Repeater for {'->'.join(str(action) for action in self.actions)}"


class AutomatingThread[T, S](Thread, LoggedComponent):
    def __init__(
        self,
        prompt_data: PromptData[T, S],
        port: str,
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
        subprocess.Popen(["curl", "-XPOST", f"localhost:{self.port}", "-d", "change-prompt(Auto-updating...> )"])
        while True:
            try:
                if not self.repeat_when(self.prompt_data):
                    continue
                subprocess.Popen(
                    shlex.join(
                        [
                            "curl",
                            "-XPOST",
                            f"localhost:{self.port}",
                            "-d",
                            Binding("", *self.actions).action_string(),
                        ]
                    ),
                    shell=True,  # ❗ required for getting FZF_PORT
                )
            except Exception as err:
                self.logger.exception(err)
                self.should_stop = True
                continue
            finally:
                if self.should_stop:
                    # TODO: reset prompt back to previous
                    subprocess.Popen(["curl", "-XPOST", f"localhost:{self.port}", "-d", "change-prompt(> )"])
                    break
                time.sleep(self.repeat_interval)
