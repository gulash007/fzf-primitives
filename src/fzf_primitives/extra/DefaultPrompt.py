from __future__ import annotations

from enum import Enum
from typing import Callable

import typer

from .. import Prompt
from ..config import Config
from ..core.FzfPrompt.exceptions import Quitting
from . import BasePrompt

app = typer.Typer()


class DefaultPrompt[T, S](Prompt[T, S]):
    def __init__(
        self,
        entries: list[T] | None = None,
        converter: Callable[[T], str] = str,
        obj: S = None,
        *,
        use_basic_hotkeys: bool | None = None,
    ):
        super().__init__(entries, converter, obj, use_basic_hotkeys=use_basic_hotkeys)
        self.mod.preview().basic
        self.mod.default


class LineInterpretation(Enum):
    DEFAULT = "default"
    PATH = "path"


@app.command()
def main(
    options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --"),
    log: bool = False,
    lines_as: LineInterpretation = LineInterpretation.DEFAULT,
):
    if log:
        Config.logging_enabled = True
    options = options or []
    try:
        prompt = DefaultPrompt(entries=BasePrompt.read_entries())
        prompt.mod.options.add(*options)
        if lines_as == LineInterpretation.PATH:
            prompt.mod.on_hotkey().CTRL_O.open_files(app="Vim")
        output = prompt.run()
    except Quitting as e:
        print(f"Exiting loop: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
