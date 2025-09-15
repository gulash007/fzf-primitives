from __future__ import annotations

import itertools
import json
from pathlib import Path

from ...FzfPrompt import Binding, Preview, PromptData
from ...FzfPrompt.action_menu.transform import Transform
from ...FzfPrompt.options import Event, Hotkey
from ...FzfPrompt.shell import shell_command
from ...monitoring import LoggedComponent


class FileViewer:
    def __init__(self, language: str = "", theme: str = "Solarized (light)", *, plain: bool = True):
        self.language = language
        self.theme = theme
        self.plain = plain

    def view(self, *files: str | Path):
        if not files:
            return "No file selected"
        command = ["bat", "--color=always"]
        if self.language:
            command.extend(("--language", self.language))
        if self.theme:
            command.extend(("--theme", self.theme))
        if self.plain:
            command.append("--plain")
        command.append("--")  # Fixes file names starting with a hyphen
        command.extend(map(str, files))
        return shell_command(command)


# HACK: ❗This object pretends to be a preview but when transform is invoked it injects its previews cyclically
# into Previewer as current previews (it's never itself a current preview except when made main preview, then it's there only until first replaced).
class CyclicalPreview[T, S](Preview[T, S], LoggedComponent):
    def __init__(self, name: str, previews: list[Preview[T, S]], trigger: Hotkey | Event | None = None):
        LoggedComponent.__init__(self)
        self._previews = itertools.cycle(previews)
        initial_preview = next(self._previews)
        super().__init__(name, **initial_preview.mutation_args)
        self.preview_change_binding = Binding(name, Transform(self.next))
        self._current_preview = initial_preview

    def next(self, prompt_data: PromptData[T, S]):
        if prompt_data.previewer.current_preview.id in (self._current_preview.id, self.id):
            next_preview = next(self._previews)
            self.logger.debug(
                f"Changing preview to next in cycle: {next_preview}",
                trace_point="cycle_preview_next",
                current_preview=self._current_preview.name,
                next_preview=next_preview.name,
            )
            self._current_preview = next_preview
        return self._current_preview.preview_change_binding.actions


def preview_basic(prompt_data: PromptData):
    return json.dumps(
        {
            "query": prompt_data.query,
            "current_index": prompt_data.current_index,
            "current": prompt_data.current,
            "selected_indices": prompt_data.selected_indices,
            "selections": prompt_data.selections,
            "target_indices": prompt_data.target_indices,
            "targets": prompt_data.targets,
        },
        indent=4,
        default=str,
    )


def get_fzf_json(prompt_data: PromptData, FZF_PORT: str):
    import json

    import requests

    return json.dumps(requests.get(f"http://127.0.0.1:{FZF_PORT}").json(), indent=2)


def get_fzf_env_vars(
    prompt_data: PromptData,
    FZF_LINES,
    FZF_COLUMNS,
    FZF_TOTAL_COUNT,
    FZF_MATCH_COUNT,
    FZF_SELECT_COUNT,
    FZF_POS,
    FZF_QUERY,
    FZF_INPUT_STATE,
    FZF_NTH,
    FZF_PROMPT,
    FZF_GHOST,
    FZF_POINTER,
    FZF_PREVIEW_LABEL,
    FZF_BORDER_LABEL,
    FZF_LIST_LABEL,
    FZF_INPUT_LABEL,
    FZF_HEADER_LABEL,
    FZF_ACTION,
    FZF_KEY,
    FZF_PORT,
    FZF_PREVIEW_TOP,
    FZF_PREVIEW_LEFT,
    FZF_PREVIEW_LINES,
    FZF_PREVIEW_COLUMNS,
):
    local_variables = locals().copy()
    local_variables.pop("prompt_data", None)
    return json.dumps(local_variables, indent=4, ensure_ascii=False, sort_keys=True)
