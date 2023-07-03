from __future__ import annotations

import typer

from . import BasePrompt, mods
from .FzfPrompt.exceptions import ExitLoop
from .FzfPrompt.options import Options
from .FzfPrompt.Prompt import Result, PromptData
from .monitoring.Logger import get_logger

logger = get_logger()

app = typer.Typer()


# TODO: add support for outputting from all available info (including preview)


@mods.on_event("ctrl-c").clip
@mods.on_event("ctrl-q").quit
@mods.exit_round_when_aborted()
def run(prompt_data: PromptData) -> Result:
    return BasePrompt.run(prompt_data=prompt_data)


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    try:
        prompt_data = PromptData(choices=BasePrompt.read_choices(), options=Options(*options))
        output = run(prompt_data)
    except ExitLoop as e:
        print(f"Exiting loop: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    logger.enable("")
    app()
