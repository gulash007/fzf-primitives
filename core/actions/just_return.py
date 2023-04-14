from typing import Optional
import typer
from ..helpers.decorators import output_to_stdin_and_return
from .helpers import supports_indexed_selections

app = typer.Typer()


def just_return(query: str, selections: list[str], indices: Optional[list[int]] = None):
    """Just returns"""
    if not indices:
        return query, selections
    return query, list(zip(indices, selections))


print_and_return = output_to_stdin_and_return(just_return)
command = supports_indexed_selections(print_and_return)
app.command()(command)

if __name__ == "__main__":
    app()
