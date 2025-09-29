from __future__ import annotations

from typing import Callable

from ....FzfPrompt import Action, PreviewFunction, PromptData, ServerCall, Transform
from ....FzfPrompt.action_menu import MovePointer, SelectAt
from ....monitoring import LoggedComponent

type EntriesGetter[T, S] = Callable[[PromptData[T, S]], list[T]]


class SelectBy[T, S](Transform[T, S], LoggedComponent):
    def __init__(self, predicate: Callable[[PromptData[T, S], T], bool]):
        LoggedComponent.__init__(self)

        def get_select_actions(prompt_data: PromptData[T, S]) -> list[Action]:
            try:
                original_position = prompt_data.state.current_index
                if original_position is None:
                    return []
                actions: list[Action] = []
                for i, entry in enumerate(prompt_data.entries):
                    try:
                        should_select = predicate(prompt_data, entry)
                    except Exception as e:
                        self.logger.warning(f"{e.__class__.__name__}: {e}", trace_point="error_in_select_by_predicate")
                        continue
                    if should_select:
                        self.logger.debug(
                            f"Selecting choice at index {i} with value: {entry}", trace_point="selecting_choice"
                        )
                        actions.append(SelectAt(i))
                actions.append(MovePointer(original_position))
                return actions
            except Exception as e:
                self.logger.error(f"Error in get_select_actions: {e}", trace_point="error_in_get_select_actions")
                return ["bell"]

        super().__init__(get_select_actions, f"Selecting by: {predicate.__name__}")

    def __str__(self) -> str:
        return f"[SB]({self._get_function_name(self.function)})"


class ReloadEntries[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, entries_getter: EntriesGetter[T, S], *, sync: bool = False):
        LoggedComponent.__init__(self)

        def reload_entries(prompt_data: PromptData[T, S]):
            try:
                entries = entries_getter(prompt_data)
                prompt_data.entries = entries
                return prompt_data.fzf_input()
            except Exception as e:
                self.logger.error(f"Error in reload_entries: {e}", trace_point="error_in_reload_entries")
                return None

        super().__init__(reload_entries, command_type="reload-sync" if sync else "reload")

    def __str__(self) -> str:
        return f"[RC]({self._get_function_name(self.function)})"


class ShowInPreview[T, S](ServerCall[T, S]):
    def __init__(self, show_in_preview: PreviewFunction[T, S], description: str | None = None):
        super().__init__(show_in_preview, description, command_type="preview")

    def __str__(self) -> str:
        return f"[SIP]({self.id})"
