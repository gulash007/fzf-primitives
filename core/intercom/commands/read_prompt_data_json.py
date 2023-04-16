# Just outputs the stored JSON

import typer

from ..PromptData import PromptData


app = typer.Typer()


@app.command()
def main(prompt_id: str):
    prompt_data_json = PromptData.read(prompt_id)
    typer.echo(prompt_data_json)


if __name__ == "__main__":
    app()
