from typing import Optional
import typer
from thingies import shell_command
from ..helpers.decorators import output_to_stdin_and_return

app = typer.Typer()


def preview_file(
    query: str,
    selections: list[str],
    indices: Optional[list[int]] = None,
    directory: str = "",
    language: str = "",
    theme: str = "",
):
    selections_as_args = " ".join(f'"{directory}/{selection}"' for selection in selections)
    language_arg = f"--language {language}" if language else ""
    theme_arg = f'--theme "{theme}"' if theme else ""
    return shell_command(f"bat --color=always {language_arg} {theme_arg} {selections_as_args}")


app.command()(output_to_stdin_and_return(preview_file))

if __name__ == "__main__":
    app()
