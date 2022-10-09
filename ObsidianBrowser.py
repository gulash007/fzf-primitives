import os
from pathlib import Path
from pyfzf import FzfPrompt
from core import mods
from core.exceptions import ExitLoop, ExitRound
from thingies import shell_command


DEFAULT_OPTS = "--layout=reverse --inline-info --cycle --no-mouse --bind alt-shift-up:preview-half-page-up,alt-shift-down:preview-half-page-down --preview-window=wrap"
VAULT_PATH = Path("/Users/honza/Documents/HOLLY")


DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")


class ObsidianBrowser:
    def __init__(self, repo_location: Path = DEFAULT_REPO_PATH) -> None:
        self.repo_location = repo_location

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        os.chdir(VAULT_PATH)
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
                return
            except Exception as e:
                print(f"{type(e).__name__}: {e}")
                return

    @mods.clip_output
    @mods.exit_on_no_selection
    def get_files_and_preview_their_content(self, options, repo_location):
        prompt = FzfPrompt()
        return prompt.prompt(choices=shell_command("ls").split("\n"), fzf_options=options)

    @mods.clip_output
    @mods.exit_on_no_selection
    @mods.ansi
    @mods.multiselect
    def get_lines_of_file(self, options, file_name):
        prompt = FzfPrompt()
        return prompt.prompt(
            choices=shell_command(f'bat "{file_name}" --color=always').split("\n"), fzf_options=options
        )


ob = ObsidianBrowser(VAULT_PATH)
ob.run()
