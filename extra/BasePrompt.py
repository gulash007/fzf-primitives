import os
import sys
from stat import S_ISFIFO

import pyperclip
import typer

from ..core.FzfPrompt import PromptData, run_fzf_prompt
from ..core.FzfPrompt.exceptions import Quitting
from ..core.FzfPrompt.options import Options

app = typer.Typer()


__all__ = ["run", "read_choices"]

run = run_fzf_prompt


# TODO: cache read choices for multiple rounds of selection
def read_from_pipe():
    return sys.stdin.read() if S_ISFIFO(os.fstat(0).st_mode) else None


def read_choices():
    if (choices := read_from_pipe()) is None:
        choices = pyperclip.paste()
    return choices.splitlines()


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    options = options or []
    try:
        output = run(prompt_data=PromptData(choices=read_choices(), options=Options(*options)))
    except Quitting as e:
        print(f"Exiting loop: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
