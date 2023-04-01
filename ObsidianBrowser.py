from pathlib import Path

from thingies import shell_command

from .core import mods
from .core.exceptions import ExitLoop, ExitRound
from .core.MyFzfPrompt import run_fzf_prompt
from .core.options import HOTKEY, POSITION, Options
from .core.previews import PREVIEW

DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")


def raise_quit(result):
    raise ExitLoop


class ObsidianBrowser:
    def __init__(self, repo_location: Path = DEFAULT_REPO_PATH) -> None:
        self.repo_location = repo_location

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        # TODO: maybe there's no need to have options
        file_name = self.get_files_and_preview_their_content()[0]
        lines = self.get_lines_of_file(file_name=file_name)
        print("\n".join(lines))

    def run_in_loop(self):
        while True:
            try:
                self.run()
            except ExitRound:
                continue
            except ExitLoop:
                print("Exiting loop")
                return
            # except Exception as e:
            #     print(f"{type(e).__name__}: {e}")
            #     return

    # @mods.clip_output
    @mods.hotkey(hk=HOTKEY.ctrl_c, action="execute(echo {} | clip)")
    @mods.hotkey(
        hk=HOTKEY.ctrl_o,
        action='execute(file_name={} && note_name=${file_name%.md} && note_name=$(echo $note_name | jq -R -r @uri) && open "obsidian://open?vault=HOLLY&file=${note_name%.md}")',
    )
    @mods.hotkey_python(hk=HOTKEY.ctrl_q, action=raise_quit)
    @Options().defaults.ansi.multiselect
    @mods.preview(PREVIEW.file(directory=DEFAULT_REPO_PATH, theme="Solarized (light)"), window_size=80)
    @mods.exit_round_on_no_selection
    def get_files_and_preview_their_content(self, options: Options = Options()):
        # print(options)
        return run_fzf_prompt(
            choices=shell_command(
                f"cd {self.repo_location} && find * -name '*.md' -not -path 'ALFRED/Personal/*'"
            ).split("\n"),
            fzf_options=options,
        )  # better file-listing cmd

    @mods.clip_output
    @mods.preview(
        command='x={} && echo "${x:9}"', window_size="2", window_position=POSITION.up, live_clip_preview=False
    )
    @mods.exit_round_on_no_selection
    @Options().defaults.no_sort.multiselect.ansi
    def get_lines_of_file(self, options: Options = Options(), file_name: str = ""):
        # print(options)
        return run_fzf_prompt(
            choices=shell_command(
                f'bat "{self.repo_location}/{file_name}" --color=always --theme "Solarized (light)"'
            ).split("\n"),
            fzf_options=options,
        )


if __name__ == "__main__":
    ob = ObsidianBrowser()
    ob.run_in_loop()
