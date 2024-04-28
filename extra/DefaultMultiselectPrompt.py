from __future__ import annotations

import typer

from ..core.FzfPrompt.exceptions import Quitting
from ..core.monitoring.Logger import get_logger
from . import BasePrompt, DefaultPrompt

logger = get_logger()

app = typer.Typer()


class DefaultMultiselectPrompt[T, S](DefaultPrompt.DefaultPrompt[T, S]):
    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        *,
        override_basic_hotkeys: bool = False,
    ):
        super().__init__(choices, presented_choices, obj, use_basic_hotkeys=override_basic_hotkeys)
        self.mod.options.multiselect
        self.mod.on_hotkey().CTRL_A.toggle_all


@app.command()
def main(
    options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --"),
    log: bool = False,
):
    if log:
        logger.enable("")
    options = options or []
    try:
        prompt = DefaultMultiselectPrompt(choices=BasePrompt.read_choices())
        prompt.mod.options.add(*options)
        output = prompt.run()
    except Quitting as e:
        print(f"Exiting loop: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
