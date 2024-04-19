from __future__ import annotations

from typing import Callable

from ..FzfPrompt.exceptions import ExitRound
from ..FzfPrompt.Prompt import PostProcessor, PromptData, Result


class PostProcessing[T, S]:
    def __init__(self) -> None:
        self._post_processors: list[PostProcessor[T, S]] = []

    def custom(self, function: Callable[[PromptData[T, S]], None]):
        self._post_processors.append(function)
        return self

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for post_processor in self._post_processors:
            prompt_data.add_post_processor(post_processor)

    # presets
    # TODO: clip presented selections or the selections passed as choices?
    def clip_output(self, transformer: Callable[[Result[T]], str] = str):
        raise NotImplementedError("clip output not implemented yet")

    # TODO: Check correctness or if it's needed
    def exit_round_on(self, predicate: Callable[[PromptData[T, S]], bool], message: str = ""):
        def exit_round_on_predicate(prompt_data: PromptData[T, S]):
            if predicate(prompt_data):
                raise ExitRound(message)

        return self.custom(exit_round_on_predicate)

    def exit_round_when_aborted(self, message: str = "Aborted!"):
        return self.exit_round_on(lambda prompt_data: prompt_data.result.end_status == "abort", message)

    def exit_round_on_empty_selections(self, message: str = "Selection empty!"):
        return self.exit_round_on(lambda prompt_data: not prompt_data.result, message)
