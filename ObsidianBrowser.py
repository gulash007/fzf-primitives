from pathlib import Path
from pyfzf import FzfPrompt
from core import mods
from core.exceptions import ExitLoop, ExitRound
from thingies import shell_command


DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")


class ObsidianBrowser:
    def __init__(self, repo_location: Path = DEFAULT_REPO_PATH) -> None:
        self.repo_location = repo_location

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        # TODO: maybe there's no need to have options
        file_name = self.get_files_and_preview_their_content("", self.repo_location)[0]
        lines = self.get_lines_of_file("", file_name)
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

    # @mods.hotkey(
    #     hotkey=HOTKEYS.ctrl_o,
    #     action='execute(file_name={} && open "obsidian://open?vault=HOLLY&file=\${file_name%.md}")',
    # )
    @mods.clip_output
    @mods.ansi
    @mods.defaults
    @mods.preview(
        command="bat %s/{} --color=always", window_size=80, formatter=lambda self, command: command % self.repo_location
    )
    @mods.exit_hotkey
    @mods.exit_on_no_selection
    def get_files_and_preview_their_content(self, options: str, repo_location: Path):
        prompt = FzfPrompt()
        return prompt.prompt(
            choices=shell_command(f'ls "{repo_location}"').split("\n"), fzf_options=options
        )  # better file-listing cmd

    @mods.clip_output
    @mods.no_sort
    @mods.ansi
    @mods.multiselect
    @mods.defaults
    @mods.preview(command='x={} && echo "${x:9}"', window_size=70, live_clip_preview=True)
    @mods.exit_on_no_selection
    @mods.exit_hotkey
    def get_lines_of_file(self, options: str, file_name: str):
        prompt = FzfPrompt()
        return prompt.prompt(
            choices=shell_command(f'bat "{self.repo_location}/{file_name}" --color=always').split("\n"),
            fzf_options=options,
        )


if __name__ == "__main__":
    ob = ObsidianBrowser()
    ob.run_in_loop()
