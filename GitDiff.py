import typer
from thingies import shell_command

from .core import BasePrompt, DefaultPrompt, mods
from .core.BasicLoop import BasicLoop
from .core.FzfPrompt.PromptData import PromptData
from .core.monitoring.Logger import get_logger

app = typer.Typer()


logger = get_logger()

# TODO: Show untracked files and their content (mark them as untracked)

# TODO: refresh selections after git add?
# TODO: ❗ --cached (multi command typer)
@mods.on_event("ctrl-6")("git add --patch", "execute(git add --patch -- {})", "refresh-preview")
def run_normally(prompt_data: PromptData):
    prompt_data.choices = shell_command(["git", "diff", "--name-only"]).splitlines()
    prompt_data.options.preview("git diff --color=always -- {}")
    return DefaultPrompt.run(prompt_data)


@mods.on_event("ctrl-6")("git reset --patch", "execute(git reset --patch -- {})", "refresh-preview")
def run_for_staged(prompt_data: PromptData):
    prompt_data.choices = shell_command(["git", "diff", "--cached", "--name-only"]).splitlines()
    prompt_data.options.preview("git diff --cached --color=always -- {}")
    return DefaultPrompt.run(prompt_data)


@app.command()
def main(staged: bool = False):
    return BasicLoop(lambda: run_for_staged(PromptData()) if staged else run_normally(PromptData())).run_in_loop()


if __name__ == "__main__":
    logger.enable("")
    app()
