import re
from pathlib import Path

from pyfzf import FzfPrompt
from thingies import shell_command

from core import mods
from core.exceptions import ExitLoop, ExitRound

DEFAULT_REPO_PATH = Path("/Users/honza/Documents/HOLLY")
WINDOW_ID_REGEX = re.compile("(?<=\[).*(?=\])")


class ChromeWindowManager:
    def __init__(self, repo_location: Path = DEFAULT_REPO_PATH) -> None:
        self.repo_location = repo_location

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        # TODO: maybe there's no need to have options
        window = self.select_window("")[0]
        window_id = self.extract_window_id(window)
        self.focus_window(window_id)

    def run_in_loop(self):
        while True:
            try:
                self.run()
            except ExitRound:
                continue
            except ExitLoop:
                print("Exiting loop")
                return

    @mods.preview(
        "source ~/.zshforchrome 2>/dev/null && echo {} | get_chrome_id | read -r window_id && chrome-cli list tabs -w $window_id",
        70,
    )
    @mods.exit_hotkey
    @mods.exit_on_no_selection
    def select_window(self, options=""):
        prompt = FzfPrompt()
        return prompt.prompt(choices=shell_command("chrome-cli list windows").split("\n"), fzf_options=options)

    def extract_window_id(self, line: str) -> str:
        return WINDOW_ID_REGEX.search(line)[0]

    def focus_window(self, window_id: str):
        shell_command(f'chrome-cli open "" -w "{window_id}"')
        new_tab_id = shell_command(
            f"source ~/.zshforchrome && chrome-cli list tabs -w \"{window_id}\" | awk 'END{{print}}' | get_chrome_id"
        )
        shell_command(f'chrome-cli close -t "{new_tab_id}"')


if __name__ == "__main__":
    cwm = ChromeWindowManager()
    cwm.run_in_loop()
