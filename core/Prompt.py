from __future__ import annotations
import pyperclip

from typing import Iterable, Self, final
import typer

from thingies import read_from_pipe
from .MyFzfPrompt import Result, run_fzf_prompt
from .options import Options

app = typer.Typer()


# TODO: add support for piping into it
# TODO: add support for processing clipboard
# TODO: add support for running it with custom choices (passed as argument)
# TODO: add support for running it with custom options (passed as argument)
# TODO: add support for accessing attributes of python objects in preview command (using dill?)
# TODO: add support for outputting from all available info (including preview)


class Prompt:
    _instance_created = False  # each subclass needs to define own _instance_created = False
    _options = Options().defaults  # define those in subclass if you want to override, otherwise they're inherited

    @final
    def __init__(self):
        if self.__class__._instance_created:
            raise RuntimeError("Instance already created")
        self.__class__._instance_created = True

    # subclasses should use Prompt(self).run in their overridden .run methods to run pyfzf prompt
    def run(self, *, choices: Iterable = None, options: Options = Options()) -> Result | Self:
        choices = choices or []
        return run_fzf_prompt(choices=choices, options=self._options + options)

    # TODO: cache read choices for multiple rounds of selection
    def read(self):
        try:
            choices = read_from_pipe().splitlines()
        except OSError:
            choices = pyperclip.paste().splitlines()
        return self.run(choices=choices)


prompt = Prompt()


@app.command()
def main():
    output = prompt.read()
    typer.echo(output, color=True)


if __name__ == "__main__":
    app()
