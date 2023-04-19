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

__all__ = ["run", "read_choices"]

run = run_fzf_prompt


# TODO: cache read choices for multiple rounds of selection
def read_choices():
    if (choices := read_from_pipe()) is None:
        choices = pyperclip.paste()
    return choices.splitlines()


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    try:
        output = run(prompt_data=PromptData(choices=read_choices(), options=Options(*options)))
    except ExitLoop as e:
        print(f"{color('Exiting loop').red.bold}: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
