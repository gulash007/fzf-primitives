from pathlib import Path

from thingies import shell_command

from .core import mods
from .core.exceptions import ExitLoop, ExitRound
from .core.MyFzfPrompt import run_fzf_prompt
from .core.Prompt import Prompt
from .core.ActionMenu import ActionMenu
from .core.BasicLoop import BasicLoop
from .core.options import HOTKEY, POSITION, Options
from .core.previews import PREVIEW

DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")


class FileSelectionPrompt(Prompt):
    _action_menu_type = ActionMenu

    def __init__(self, dirpath: Path) -> None:
        super().__init__()
        self._dirpath = dirpath

    # @mods.clip_output
    @mods.hotkey(
        hk=HOTKEY.ctrl_o,
        action='execute(file_name={} && note_name=${file_name%.md} && note_name=$(echo $note_name | jq -R -r @uri) && open "obsidian://open?vault=HOLLY&file=${note_name%.md}")',
    )
    @Options().defaults.ansi.multiselect
    @mods.preview(PREVIEW.file(directory=DEFAULT_REPO_PATH, theme="Solarized (light)"), window_size=80)
    def __call__(self, options: Options = Options()):
        # print(options)
        return run_fzf_prompt(
            choices=shell_command(f"cd {self._dirpath} && find * -name '*.md' -not -path 'ALFRED/Personal/*'").split(
                "\n"
            ),
            fzf_options=self._options + options,
        )  # better file-listing cmd


class FileBrowserPrompt(Prompt):
    _action_menu_type = ActionMenu

    def __init__(self, file_path: Path) -> None:
        super().__init__()
        self._file_path = file_path

    @mods.clip_output
    @mods.preview(
        command='x={} && echo "${x:9}"', window_size="2", window_position=POSITION.up, live_clip_preview=False
    )
    @Options().defaults.no_sort.multiselect.ansi
    def __call__(self, options: Options = Options(), file_name: str = ""):
        # print(options)
        return run_fzf_prompt(
            choices=shell_command(f'bat "{self._file_path}" --color=always --theme "Solarized (light)"').split("\n"),
            fzf_options=self._options + options,
        )


class ObsidianBrowser(BasicLoop):
    def __init__(self, repo_location: Path = DEFAULT_REPO_PATH) -> None:
        self.repo_location = repo_location
        self.get_files_and_preview_their_content = FileSelectionPrompt(self.repo_location)

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        # TODO: maybe there's no need to have options
        file_name = self.get_files_and_preview_their_content()[0]
        file_path = self.repo_location.joinpath(file_name)
        lines = FileBrowserPrompt(file_path)()
        print("\n".join(lines))


if __name__ == "__main__":
    ob = ObsidianBrowser()
    ob.run_in_loop()
