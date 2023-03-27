import typer

app = typer.Typer()


@app.command()
def preview_basic(query: str, selections: list[str]):
    sep = "\n\t"
    typer.echo(f"query: {query}\nselections:\n\t{sep.join(selections)}")


if __name__ == "__main__":
    app()
