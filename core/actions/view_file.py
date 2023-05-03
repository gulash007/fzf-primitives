from thingies import shell_command

from .helpers import EMPTY_SELECTION, CommandCreator

app = CommandCreator()


@app.register_command()
def view_file(
    query: str,
    selections: list[str],
    language: str = "",
    theme: str = "",
):
    if selections == EMPTY_SELECTION:
        selections = []
    command = ["bat", "--color=always"]
    if language:
        command.extend(("--language", language))
    if theme:
        command.extend(("--theme", theme))
    command.append("--")  # Fixes file names starting with a hyphen
    command.extend(selections)
    return shell_command(command)


if __name__ == "__main__":
    app()
