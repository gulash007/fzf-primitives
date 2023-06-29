import typer
from thingies import shell_command

from .core import BasePrompt, DefaultPrompt, mods
from .core import BasicLoop
from .core.FzfPrompt.Prompt import PromptData, ShellCommand
from .core.monitoring.Logger import get_logger

app = typer.Typer()


logger = get_logger()


# TODO: Show untracked files and their content (mark them as untracked)
# TODO: refresh selections after git add?
# TODO: ❗ --cached (multi command typer)
@mods.on_event("ctrl-6").run("git add --patch", ShellCommand("git add --patch -- {}"), "refresh-preview")
def run_normally(prompt_data: PromptData):
    prompt_data.choices = shell_command(["git", "diff", "--name-only"]).splitlines()
    prompt_data.options.preview("git diff --color=always -- {}")
    return DefaultPrompt.run(prompt_data)


@mods.on_event("ctrl-6").run("git reset --patch", ShellCommand("git reset --patch -- {}"), "refresh-preview")
def run_for_staged(prompt_data: PromptData):
    prompt_data.choices = shell_command(["git", "diff", "--cached", "--name-only"]).splitlines()
    prompt_data.options.preview("git diff --cached --color=always -- {}")
    return DefaultPrompt.run(prompt_data)


@app.command()
def main(staged: bool = False, commitish: str = ""):
    return BasicLoop.run_in_loop(lambda: run_for_staged(PromptData()) if staged else run_normally(PromptData()))


if __name__ == "__main__":
    logger.enable("")
    app()
