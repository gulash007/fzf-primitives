from __future__ import annotations

import typer
from thingies import color

from . import BasePrompt, mods
from .exceptions import ExitLoop
from .FzfPrompt.options import Options
from .FzfPrompt.Prompt import Result
from .FzfPrompt.PromptData import PromptData

app = typer.Typer()


# TODO: add support for outputting from all available info (including preview)
def quit_app(result: Result):
    raise ExitLoop


@mods.action.toggle_all("ctrl-a")
@mods.action.clip("ctrl-c")
@mods.action_python("ctrl-q", quit_app)
@mods.exit_round_on_no_selection()
def run(prompt_data: PromptData) -> Result:
    return BasePrompt.run(prompt_data=prompt_data)


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    try:
        prompt_data = PromptData(choices=BasePrompt.read_choices(), options=Options(*options))
        output = run(prompt_data)
    except ExitLoop as e:
        print(f"{color('Exiting loop').red.bold}: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
