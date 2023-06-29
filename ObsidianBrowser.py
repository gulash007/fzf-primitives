import contextlib
import functools
from pathlib import Path
from typing import Optional

import typer
from thingies import shell_command, url_encode

from .core import DefaultPrompt, mods
from .core import BasicLoop
from .core.FzfPrompt.options import Options
from .core.FzfPrompt.Prompt import PromptData, ServerCall

DEFAULT_VAULT_NAME = "HOLLY"
DEFAULT_VAULT_PATH = Path("/Users/honza/Documents/HOLLY")


app = typer.Typer()


def obsidian_open_files(prompt_data: PromptData, query: str, selections: list[str]):
    for selection in selections:
        note_name = url_encode(Path(selection).stem)
        command = [
            "open",
            f"obsidian://advanced-uri?vault={DEFAULT_VAULT_NAME}&commandid=workspace%253Anew-tab",
            f"obsidian://open?vault={DEFAULT_VAULT_NAME}&file={note_name}",
        ]
        shell_command(command)


# @mods.clip_output
@mods.on_event("ctrl-o").run("Obsidian: Open file", ServerCall(obsidian_open_files))
@mods.ansi
@mods.multiselect
@mods.preview("ctrl-y").file(language="markdown")
def run_folder_browser_prompt(prompt_data: PromptData, dirpath: Path = DEFAULT_VAULT_PATH):
    prompt_data.choices = shell_command(
        f"cd {dirpath} && find . -name '*.md' -not -path 'ALFRED/Personal/*' | sed 's#^\\./##'"
    ).split("\n")
    return DefaultPrompt.run(prompt_data)  # better file-listing cmd


# TODO: extraction actions (like commands, links,…)
# @mods.clip_output
# @mods.preview(command='x=({+}); for line in "${x[@]}"; do echo "$line"; done', window_size=35, window_position="down")
@mods.add_options(Options().no_sort.multiselect.ansi)
def run_file_browser_prompt(prompt_data: PromptData, file_path: Path = DEFAULT_VAULT_PATH):
    prompt_data.choices = shell_command(f'bat "{file_path}" --plain --color=always --theme "Solarized (light)"').split(
        "\n"
    )
    return DefaultPrompt.run(prompt_data)


def run(vault_path: Path = DEFAULT_VAULT_PATH):
    """Runs one round of the application until end state. Loop should be implemented externally"""
    result = run_folder_browser_prompt(PromptData(), dirpath=vault_path)
    file_name = result[0]
    file_path = vault_path.joinpath(file_name)
    lines = run_file_browser_prompt(PromptData(), file_path=file_path)
    print("\n".join(lines))


@app.command()
def main(path: Optional[Path] = None):
    path = path or DEFAULT_VAULT_PATH
    with contextlib.chdir(path):
        BasicLoop.run_in_loop(functools.partial(run, path))


if __name__ == "__main__":
    app()
