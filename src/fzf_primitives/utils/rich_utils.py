from __future__ import annotations

from io import StringIO
from typing import Literal

from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.util import ClassNotFound
from rich.console import Console
from rich.syntax import Syntax


def syntax_highlight(
    text: str,
    language: str | None = None,
    filename: str | None = None,
    theme: CodeTheme = "dracula",
    width: int | None = None,
    line_numbers: bool = False,
) -> str:
    if not language:
        lexer = None
        if filename:
            try:
                lexer = guess_lexer_for_filename(filename, text)  # use Pygments to guess language from filename
            except ClassNotFound:
                pass
        if not lexer:
            lexer = guess_lexer(text)  # use Pygments to guess language from file content
        language = lexer.aliases[0]
    syntax = Syntax(text, language, theme=theme, line_numbers=line_numbers)
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
