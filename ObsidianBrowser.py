import functools
from pathlib import Path
import sys

from thingies import shell_command

from .core import DefaultPrompt as default_prompt
from .core import mods
from .core.BasicLoop import BasicLoop
from .core.DefaultActionMenu import DefaultActionMenu
from .core.options import HOTKEY, POSITION, Options
from .core.previews import PREVIEW

DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")
repo_path = Path(sys.argv[1]) if len(sys.argv) == 2 and __name__ == "__main__" else DEFAULT_REPO_PATH


# @mods.clip_output
@mods.hotkey(
    hk=HOTKEY.ctrl_o,
    action='execute(file_name={} && note_name=${file_name%.md} && note_name=$(echo $note_name | jq -R -r @uri) && open "obsidian://open?vault=HOLLY&file=${note_name%.md}")',
)
@Options().ansi.multiselect
@mods.preview(PREVIEW.file(directory=repo_path, theme="Solarized (light)"), window_size=80)
@mods.exit_round_on_no_selection()
@DefaultActionMenu()
def run_folder_browser_prompt(options: Options = Options(), dirpath: Path = DEFAULT_REPO_PATH):
    return default_prompt.run(
        choices=shell_command(
            f"cd {dirpath} && find . -name '*.md' -not -path 'ALFRED/Personal/*' | sed 's#^\\./##'"
        ).split("\n"),
        options=options,
    )  # better file-listing cmd


@mods.clip_output
@mods.preview(command='x={} && echo "${x:9}"', window_size="2", window_position=POSITION.up, live_clip_preview=False)
@Options().no_sort.multiselect.ansi
def run_file_browser_prompt(options: Options = Options(), file_path: Path = DEFAULT_REPO_PATH):
    return default_prompt.run(
        choices=shell_command(f'bat "{file_path}" --color=always --theme "Solarized (light)"').split("\n"),
        options=options,
    )


def run(repo_location: Path = DEFAULT_REPO_PATH):
    """Runs one round of the application until end state. Loop should be implemented externally"""
    result = run_folder_browser_prompt(dirpath=repo_location)
    file_name = result[0]
    file_path = repo_location.joinpath(file_name)
    lines = run_file_browser_prompt(file_path=file_path)
    print("\n".join(lines))


if __name__ == "__main__":
    BasicLoop(functools.partial(run, repo_path)).run_in_loop()
