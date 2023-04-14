import typer
from thingies import shell_command, url_encode
from pathlib import Path

app = typer.Typer()


def obsidian_open_files(query: str, selections: list[str], vault_name: str = "HOLLY"):
    for selection in selections:
        note_name = url_encode(Path(selection).stem)
        command = [
            "open",
            f"obsidian://advanced-uri?vault={vault_name}&commandid=workspace%253Anew-tab",
            f"obsidian://open?vault={vault_name}&file={note_name}",
        ]
        shell_command(command)


app.command()(obsidian_open_files)

if __name__ == "__main__":
    app()
