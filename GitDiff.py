from .core.FzfPrompt.PromptData import PromptData
from thingies import shell_command
from .core import BasePrompt, mods, DefaultPrompt
from .core.monitoring.Logger import get_logger
import typer

app = typer.Typer()


logger = get_logger()


# TODO: refresh selections after git add?
# TODO: ❗ --cached (multi command typer)
@mods.action.custom("git add --patch", "execute(git add --patch -- {})+refresh-preview", "ctrl-6")
def run_normally(prompt_data: PromptData):
    prompt_data.choices = shell_command(["git", "diff", "--name-only"]).splitlines()
    prompt_data.options.preview("git diff --color=always -- {}")
    return DefaultPrompt.run(prompt_data)


@mods.action.custom("git reset --patch", "execute(git reset --patch -- {})+refresh-preview", "ctrl-6")
def run_for_staged(prompt_data: PromptData):
    prompt_data.choices = shell_command(["git", "diff", "--cached", "--name-only"]).splitlines()
    prompt_data.options.preview("git diff --cached --color=always -- {}")
    return DefaultPrompt.run(prompt_data)


@app.command()
def main(staged: bool = False):
    return run_for_staged(PromptData()) if staged else run_normally(PromptData())


if __name__ == "__main__":
    app()
