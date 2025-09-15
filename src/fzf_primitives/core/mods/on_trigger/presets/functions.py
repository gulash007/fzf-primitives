# clip current preview
from __future__ import annotations

from typing import Callable

import pyperclip

from ....FzfPrompt import PromptData


def clip_current_preview(prompt_data: PromptData, converter: Callable[[str], str] | None = None):
    preview_str = prompt_data.get_current_preview()
    if converter:
        preview_str = converter(preview_str)
    pyperclip.copy(preview_str)


# clip options
def clip_options(prompt_data: PromptData):
    pyperclip.copy(str(prompt_data.options))
