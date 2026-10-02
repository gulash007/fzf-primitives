# open file in editor
from typing import Literal

type FileEditor = Literal["VS Code", "VS Code - Insiders", "Emacs", "Vi", "Vim", "NeoVim", "Nano"]
FILE_EDITORS: dict[FileEditor, list[str]] = {
    "VS Code": ["code"],
    "VS Code - Insiders": ["code-insiders"],
    "Emacs": ["emacs", "-nw"],
    "Vi": ["vi"],
    "Vim": ["vim"],
    "NeoVim": ["nvim"],
    "Nano": ["nano"],
}
