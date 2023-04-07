from pathlib import Path

from thingies import shell_command

if __name__ == "__main__":
    __package__ = "fzf_primitives.experimental"

from .core import mods
from .core.BasicLoop import BasicLoop
from .core.DefaultActionMenu import DefaultActionMenu
from .core import DefaultPrompt as default_prompt
from .core.options import HOTKEY, POSITION, Options
from .core.previews import PREVIEW

DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")


# @mods.clip_output
@mods.hotkey(
    hk=HOTKEY.ctrl_o,
    action='execute(file_name={} && note_name=${file_name%.md} && note_name=$(echo $note_name | jq -R -r @uri) && open "obsidian://open?vault=HOLLY&file=${note_name%.md}")',
)
@Options().ansi.multiselect
@mods.preview(PREVIEW.file(directory=DEFAULT_REPO_PATH, theme="Solarized (light)"), window_size=80)
@mods.exit_round_on_no_selection()
@DefaultActionMenu()
def run_folder_browser_prompt(options: Options = Options(), dirpath: Path = DEFAULT_REPO_PATH):
    # print(options)
    return default_prompt.run(
        choices=shell_command(f"cd {dirpath} && find * -name '*.md' -not -path 'ALFRED/Personal/*'").split("\n"),
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


class ObsidianBrowser(BasicLoop):
    def __init__(self, repo_location: Path = DEFAULT_REPO_PATH) -> None:
        self.repo_location = repo_location

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        result = run_folder_browser_prompt(dirpath=self.repo_location)
        file_name = result[0]
        file_path = self.repo_location.joinpath(file_name)
        lines = run_file_browser_prompt(file_path=file_path)
        print("\n".join(lines))


if __name__ == "__main__":
    ob = ObsidianBrowser()
    ob.run_in_loop()
