from .functions import preview_basic
import typer

app = typer.Typer()


@app.command()
def main(query: str, selection: str, selections: list[str]):
    typer.echo(preview_basic(query, selection, selections))


if __name__ == "__main__":
    app()
