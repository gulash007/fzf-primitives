from __future__ import annotations

from typing import Callable

from ..FzfPrompt import PostProcessor, PromptData, Result
from ..FzfPrompt.exceptions import Aborted


class PostProcessing[T, S]:
    def __init__(self) -> None:
        self._post_processors: list[PostProcessor[T, S]] = []

    def custom(self, function: Callable[[PromptData[T, S]], None]):
        self._post_processors.append(function)
        return self

    def __call__(self, prompt_data: PromptData[T, S]) -> None:
        for post_processor in self._post_processors:
            prompt_data.post_processors.append(post_processor)

    # presets
    # TODO: clip presented selections or the selections passed as choices?
    def clip_output(self, transformer: Callable[[Result[T, S]], str] = str):
        raise NotImplementedError("clip output not implemented yet")

    # TODO: Check correctness or if it's needed
    def raise_aborted_on(self, predicate: Callable[[PromptData[T, S]], bool], message: str = ""):
        def raise_aborted_on_predicate(prompt_data: PromptData[T, S]):
            if predicate(prompt_data):
                raise Aborted(message, prompt_data.result)

        return self.custom(raise_aborted_on_predicate)

    def raise_from_aborted_status(self, message: str = "Aborted!"):
        return self.raise_aborted_on(lambda prompt_data: prompt_data.result.end_status == "abort", message)

    def raise_aborted_on_empty_selections(self, message: str = "Selection empty!"):
        return self.raise_aborted_on(lambda prompt_data: not prompt_data.result, message)
