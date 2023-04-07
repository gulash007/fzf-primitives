from typing import Optional
from ..helpers.decorators import output_to_stdin_and_return
from .helpers import supports_indexed_selections
import typer

app = typer.Typer()


def preview_basic(query: str, selections: list[str], indices: Optional[list[int]] = None):
    sep = "\n\t"
    if indices:
        selections = [f"{index}\t{selection}" for index, selection in zip(indices, selections)]
    return f"query: {query}\nselections:\n\t{sep.join(selections)}"


print_preview_basic = output_to_stdin_and_return(preview_basic)
command = supports_indexed_selections(print_preview_basic)
app.command()(command)

if __name__ == "__main__":
    app()
