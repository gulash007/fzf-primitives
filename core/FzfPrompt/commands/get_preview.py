import typer
from .functions import get_preview

app = typer.Typer()


@app.command()
def main(prompt_id: str, preview_id: str):
    print(get_preview(prompt_id, preview_id))


if __name__ == "__main__":
    app()
