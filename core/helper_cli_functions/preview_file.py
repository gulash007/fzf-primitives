import typer
from thingies import shell_command

app = typer.Typer()


@app.command()
def preview_file(query: str, selections: list[str], directory: str = "", language: str = "", theme: str = ""):
    if directory and not directory.endswith("/"):
        directory = f"{directory}/"
    selections_as_args = " ".join(f'"{directory}{selection}"' for selection in selections)
    language_arg = f"--language {language}" if language else ""
    theme_arg = f'--theme "{theme}"' if theme else ""
    typer.echo(shell_command(f"bat --color=always {language_arg} {theme_arg} {selections_as_args}"), color=True)


if __name__ == "__main__":
    app()
