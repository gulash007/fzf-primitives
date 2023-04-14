import contextlib
import functools
from pathlib import Path
from typing import Optional

import typer
from thingies import shell_command

from .core import DefaultPrompt, mods
from .core.actions.actions import ACTION
from .core.BasicLoop import BasicLoop
from .core.DefaultActionMenu import DefaultActionMenu
from .core.options import HOTKEY, POSITION, Options
from .core.previews import PREVIEW

DEFAULT_VAULT_PATH = Path("/Users/honza/Documents/HOLLY")


app = typer.Typer()


# @mods.clip_output
@mods.hotkey(hk=HOTKEY.ctrl_o, action=ACTION.obsidian_open_files)
@Options().ansi.multiselect
@mods.preview(PREVIEW.file(theme="Solarized (light)"), window_size=80)
@mods.exit_round_on_no_selection()
def run_folder_browser_prompt(options: Options = Options(), dirpath: Path = DEFAULT_VAULT_PATH):
    return DefaultPrompt.run(
        choices=shell_command(
            f"cd {dirpath} && find . -name '*.md' -not -path 'ALFRED/Personal/*' | sed 's#^\\./##'"
        ).split("\n"),
        options=options,
    )  # better file-listing cmd


@mods.clip_output
@mods.preview(command='x={} && echo "${x:9}"', window_size="2", window_position=POSITION.up, live_clip_preview=False)
@Options().no_sort.multiselect.ansi
def run_file_browser_prompt(options: Options = Options(), file_path: Path = DEFAULT_VAULT_PATH):
    return DefaultPrompt.run(
        choices=shell_command(f'bat "{file_path}" --color=always --theme "Solarized (light)"').split("\n"),
        options=options,
    )


def run(vault_path: Path = DEFAULT_VAULT_PATH):
    """Runs one round of the application until end state. Loop should be implemented externally"""
    result = run_folder_browser_prompt(dirpath=vault_path)
    file_name = result[0]
    file_path = vault_path.joinpath(file_name)
    lines = run_file_browser_prompt(file_path=file_path)
    print("\n".join(lines))


@app.command()
def main(path: Optional[Path] = None):
    path = path or DEFAULT_VAULT_PATH
    with contextlib.chdir(path):
        BasicLoop(functools.partial(run, path)).run_in_loop()


if __name__ == "__main__":
    app()
