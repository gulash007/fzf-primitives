import typer
from thingies import shell_command

app = typer.Typer()


@app.command()
def preview_file(language: str, query: str, selections: list[str]):
    selections_as_args = " ".join(f'"{selection}"' for selection in selections)
    typer.echo(shell_command(f"bat --color=always --language {language} {selections_as_args}"), color=True)


if __name__ == "__main__":
    app()
