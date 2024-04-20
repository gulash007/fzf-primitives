import pyperclip
import typer
from thingies import read_from_pipe

from .FzfPrompt import PromptData, run_fzf_prompt
from .FzfPrompt.exceptions import ExitLoop
from .FzfPrompt.options import Options

app = typer.Typer()


__all__ = ["run", "read_choices"]

run = run_fzf_prompt


# TODO: cache read choices for multiple rounds of selection
def read_choices():
    if (choices := read_from_pipe()) is None:
        choices = pyperclip.paste()
    return choices.splitlines()


@app.command()
def main(options: list[str] = typer.Argument(None, help="fzf options passed as string. Pass them after --")):
    options = options or []
    try:
        output = run(prompt_data=PromptData(choices=read_choices(), options=Options(*options)))
    except ExitLoop as e:
        print(f"Exiting loop: {e}")
        exit(0)
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
