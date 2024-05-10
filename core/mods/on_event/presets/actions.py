from __future__ import annotations

from typing import Callable

from ....FzfPrompt import ChoicesAndLinesMismatch, PromptData, ServerCall

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