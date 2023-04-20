from .functions import preview_basic
import typer

app = typer.Typer()


@app.command()
def main(query: str, selections: list[str]):
    typer.echo(preview_basic(query, selections))


if __name__ == "__main__":
    app()
