from __future__ import annotations

from typing import Iterable, Self

import typer

from . import mods
from .ActionMenu import ActionMenu
from .MyFzfPrompt import Result, run_fzf_prompt
from .options import Options
from .previews import PREVIEW
from .Prompt import Prompt

app = typer.Typer()
action_menu = ActionMenu()

# TODO: add support for piping into it
# TODO: add support for processing clipboard
# TODO: add support for running it with custom choices (passed as argument)
# TODO: add support for running it with custom options (passed as argument)
# TODO: add support for accessing attributes of python objects in preview command (using dill?)
# TODO: add support for outputting from all available info (including preview)


class DefaultPrompt(Prompt):
    _instance_created = False

    @mods.preview(PREVIEW.basic)
    @mods.exit_round_on_no_selection()
    @action_menu
    def run(self, *, choices: Iterable = None, options: Options = Options()) -> Result | Self:
        choices = choices or []
        return run_fzf_prompt(choices=choices, options=self._options + options)


default_prompt = DefaultPrompt()
action_menu.attach(default_prompt)


@app.command()
def main():
    output = default_prompt.read()
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
