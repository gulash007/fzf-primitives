from __future__ import annotations


import typer

from . import mods
from .DefaultActionMenu import DefaultActionMenu
from .MyFzfPrompt import Result
from .options import Options
from .previews import PREVIEW
from .Prompt import prompt

app = typer.Typer()
action_menu = DefaultActionMenu()

# TODO: add support for piping into it
# TODO: add support for processing clipboard
# TODO: add support for running it with custom choices (passed as argument)
# TODO: add support for running it with custom options (passed as argument)
# TODO: add support for accessing attributes of python objects in preview command (using dill?)
# TODO: add support for outputting from all available info (including preview)


@mods.preview(PREVIEW.basic)
@mods.exit_round_on_no_selection()
@action_menu
def run(options: Options = Options(), choices=None) -> Result:
    choices = choices or []
    return prompt.run(choices=choices, options=options)


@app.command()
def main():
    output = run(choices=prompt.read())
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
