from __future__ import annotations

from typing import Callable

from ....FzfPrompt import PreviewFunction, PromptData, ServerCall
from ....monitoring import LoggedComponent

type EntriesGetter[T, S] = Callable[[PromptData[T, S]], list[T]]


class ReloadEntries[T, S](ServerCall[T, S], LoggedComponent):
    def __init__(self, entries_getter: EntriesGetter[T, S], *, sync: bool = False):
        LoggedComponent.__init__(self)

        def reload_entries(prompt_data: PromptData[T, S]):
            try:
                entries = entries_getter(prompt_data)
                prompt_data.entries = entries
                return "\n".join([prompt_data.converter(entry) for entry in entries])
            except Exception as e:
                self.logger.error(f"Error in reload_choices: {e}")
                return None

        super().__init__(reload_entries, command_type="reload-sync" if sync else "reload")

    def __str__(self) -> str:
        return f"[RC]({self._get_function_name(self.endpoint.function)})"


class ShowInPreview[T, S](ServerCall[T, S]):
    def __init__(self, show_in_preview: PreviewFunction[T, S], description: str | None = None):
        super().__init__(show_in_preview, description, command_type="preview")

    def __str__(self) -> str:
        return f"[SIP]({self.id})"
