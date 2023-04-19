from __future__ import annotations


if __name__ == "__main__":
    __package__ = "fzf_primitives.experimental.core"

import typer
from thingies import color

from . import Prompt, mods
from .intercom.PromptData import PromptData
from .actions.actions import ACTION
from .DefaultActionMenu import DefaultActionMenu
from .exceptions import ExitLoop
from .MyFzfPrompt import Result
from .options import HOTKEY, Options
from .previews import PREVIEW

app = typer.Typer()
action_menu = DefaultActionMenu()

# TODO: add support for piping into it
# TODO: add support for processing clipboard
# TODO: add support for running it with custom choices (passed as argument)
# TODO: add support for running it with custom options (passed as argument)
# TODO: add support for accessing attributes of python objects in preview command (using dill?)
# TODO: add support for outputting from all available info (including preview)


@action_menu
# @mods.hotkey(HOTKEY.ctrl_alt_c, ACTION.clip_preview)
@mods.preview(PREVIEW.basic)
@mods.exit_round_on_no_selection()
def run(prompt_data: PromptData) -> Result:
    return Prompt.run(prompt_data=prompt_data)


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    try:
        prompt_data = PromptData(choices=Prompt.read_choices(), options=Options(*options))
        output = run(prompt_data)
    except ExitLoop as e:
        print(f"{color('Exiting loop').red.bold}: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
