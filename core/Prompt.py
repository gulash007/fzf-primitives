import shlex
from typing import Iterable

from datetime import datetime
import pyperclip
import typer
from .intercom.PromptData import PromptData
from thingies import read_from_pipe, color

from .exceptions import ExitLoop
from .MyFzfPrompt import Result, run_fzf_prompt
from .options import Options

app = typer.Typer()

# TODO: add support for piping into it
# TODO: add support for processing clipboard
# TODO: add support for running it with custom choices (passed as argument)
# TODO: add support for running it with custom options (passed as argument)
# TODO: add support for accessing attributes of python objects in preview command (using dill?)
# TODO: add support for outputting from all available info (including preview)


def run(choices: Iterable | None = None, prompt_data: PromptData | None = None, options: Options = Options()) -> Result:
    prompt_data = prompt_data or PromptData(id=datetime.now().isoformat())
    choices = choices or []
    prompt_data.choices.extend(choices)
    for preview in prompt_data.previews.values():
        options = options.add(shlex.join(shlex.split(f"--preview '{preview.command}'")))
    options = Options().defaults + options

    prompt_data.save()

    return run_fzf_prompt(choices=choices, options=options)


# TODO: cache read choices for multiple rounds of selection
def read_choices():
    if (choices := read_from_pipe()) is None:
        choices = pyperclip.paste()
    return choices.splitlines()


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    output = run(choices=read_choices(), options=Options(*options))
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
