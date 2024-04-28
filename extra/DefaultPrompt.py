from __future__ import annotations

from enum import Enum

import typer

from .. import Prompt
from ..core.FzfPrompt.exceptions import Quitting
from ..core.monitoring.Logger import get_logger
from . import BasePrompt

logger = get_logger()

app = typer.Typer()


class DefaultPrompt[T, S](Prompt[T, S]):
    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        *,
        use_basic_hotkeys: bool | None = None,
    ):
        super().__init__(choices, presented_choices, obj, use_basic_hotkeys=use_basic_hotkeys)
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
        logger.enable("")
    options = options or []
    try:
        prompt = DefaultPrompt(choices=BasePrompt.read_choices())
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
