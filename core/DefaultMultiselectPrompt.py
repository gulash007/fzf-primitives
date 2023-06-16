from __future__ import annotations

import typer
from thingies import color

from . import BasePrompt, mods
from .FzfPrompt.exceptions import ExitLoop
from .FzfPrompt.options import Options
from .FzfPrompt.Prompt import Result, PromptData
from . import DefaultPrompt

app = typer.Typer()


@mods.on_event("ctrl-a").toggle_all
@mods.multiselect
def run(prompt_data: PromptData) -> Result:
    return DefaultPrompt.run(prompt_data=prompt_data)


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
