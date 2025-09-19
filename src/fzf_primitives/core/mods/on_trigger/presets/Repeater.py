from __future__ import annotations

import time
from threading import Thread
from typing import Callable

from ....FzfPrompt import Action, Binding, PromptData
from ....FzfPrompt.action_menu import ParametrizedAction
from ....monitoring import LoggedComponent


# repeat actions
class Repeater[T, S]:
    def __init__(
        self,
        *actions: Action[T, S],
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
        *actions: Action[T, S],
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
