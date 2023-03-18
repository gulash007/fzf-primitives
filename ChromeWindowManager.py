import re

from pyfzf import FzfPrompt
from thingies import shell_command

from core import mods
from core.exceptions import ExitLoop, ExitRound

WINDOW_ID_REGEX = re.compile("(?<=\[).*(?=\])")


class ChromeWindowManager:
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
    @mods.exit_on_no_selection
    @mods.exit_hotkey
    def select_window(self, options=""):
        prompt = FzfPrompt()
        return prompt.prompt(
            choices=sorted(shell_command("chrome-cli list windows").split("\n"), key=lambda x: x.split("]")[1]),
            fzf_options=options,
        )

    def extract_window_id(self, line: str) -> str:
        return WINDOW_ID_REGEX.search(line)[0]

    def focus_window(self, window_id: str):
        active_tab_id = shell_command(f"brotab active | grep {window_id} | awk '{{ print $1 }}'")
        shell_command(f'open -a "Google Chrome" && brotab activate {active_tab_id} --focused')

if __name__ == "__main__":
    cwm = ChromeWindowManager()
    cwm.run_in_loop()
