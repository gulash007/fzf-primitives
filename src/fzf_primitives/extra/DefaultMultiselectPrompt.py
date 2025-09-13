from __future__ import annotations

from typing import Callable

import typer

from ..config import Config
from . import BasePrompt, DefaultPrompt

app = typer.Typer()


class DefaultMultiselectPrompt[T, S](DefaultPrompt.DefaultPrompt[T, S]):
    def __init__(
        self,
        entries: list[T] | None = None,
        converter: Callable[[T], str] = str,
        obj: S = None,
        *,
        override_basic_hotkeys: bool = False,
    ):
        super().__init__(entries, converter, obj, use_basic_hotkeys=override_basic_hotkeys)
        self.mod.options.multiselect
        self.mod.on_hotkey().CTRL_A.toggle_all


@app.command()
def main(
    options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --"),
    log: bool = False,
):
    if log:
        Config.logging_enabled = True
    options = options or []
    prompt = DefaultMultiselectPrompt(entries=BasePrompt.read_entries())
    prompt.mod.options.add(*options)
    output = prompt.run()
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
