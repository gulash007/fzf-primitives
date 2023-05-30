import contextlib
import functools
from pathlib import Path
from typing import Optional

import typer
from thingies import shell_command

from .core import DefaultPrompt, mods
from .core.actions.actions import ACTION
from .core.BasicLoop import BasicLoop
from .core.FzfPrompt.options import Options
from .core.FzfPrompt.PromptData import PromptData

DEFAULT_VAULT_PATH = Path("/Users/honza/Documents/HOLLY")


app = typer.Typer()


# @mods.clip_output
@mods.on_event("ctrl-o")("Obsidian: Open file", ACTION.obsidian_open_files)
@mods.ansi
@mods.multiselect
@mods.preview.file(language="markdown")("ctrl-y", window_size="80%")
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
        BasicLoop(functools.partial(run, path)).run_in_loop()


if __name__ == "__main__":
    app()
