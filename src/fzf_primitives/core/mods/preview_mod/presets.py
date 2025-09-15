from __future__ import annotations

import itertools
import json
from io import StringIO
from pathlib import Path
from typing import Literal

from pygments.lexers import guess_lexer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ...FzfPrompt import Binding, Preview, PromptData
from ...FzfPrompt.action_menu.transform import Transform
from ...FzfPrompt.options import Event, Hotkey
from ...monitoring import LoggedComponent


class FileViewer:
    def __init__(self, language: str = "", theme: CodeTheme = "dracula", plain: bool = True):
        self.language = language
        self.theme = theme
        self.plain = plain

    def view(self, *paths: str | Path, width: int | None = None):
        if not paths:
            return "No file selected"
        outputs = []
        proper_paths = [Path(p) if not isinstance(p, Path) else p for p in paths]
        for path in proper_paths:
            if path.is_file():
                outputs.append(self.prettify(path.read_text(encoding="utf-8", errors="ignore"), width))
            elif path.is_dir():
                outputs.append("Cannot preview directory...")
            else:
                return f"Cannot preview: {path} (not a file or directory)"

        if len(outputs) > 1:
            for output, path in zip(outputs, proper_paths, strict=True):
                header = f"{'Directory' if path.is_dir() else 'File'}: {str(path)}"
                outputs[outputs.index(output)] = (
                    f"{render_to_string(Panel(header, style='bold cyan', box=box.HEAVY))}\n{output}"
                )
        return "\n".join(outputs)

    def prettify(self, text: str, width: int | None = None) -> str:
        if self.language:
            language = self.language
        else:
            lexer = guess_lexer(text)  # use Pygments to guess language from file content
            language = lexer.aliases[0]
        syntax = Syntax(text, language, theme=self.theme, line_numbers=not self.plain)
        return render_to_string(syntax, width)


def render_to_string(renderable, width: int | None = None) -> str:
    buffer = StringIO()
    console = Console(file=buffer, width=width, force_terminal=True, color_system="truecolor")
    console.print(renderable)
    return buffer.getvalue()


CodeTheme = Literal[
    "lightbulb",
    "github-dark",
    "monokai",
    "dracula",
    "solarized-dark",
    "vim",
    "nord",
    "material",
    "one-dark",
    "nord-darker",
    "gruvbox-dark",
    "stata-dark",
    "paraiso-dark",
    "coffee",
    "native",
    "inkpot",
    "fruity",
]


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
