import re
import time

from thingies import shell_command

from .core import mods
from .core.Prompt import Prompt
from .core.ActionMenu import ActionMenu
from .core.exceptions import ExitLoop, ExitRound
from .core.MyFzfPrompt import Result, run_fzf_prompt
from .core.options import Options, HOTKEY

WINDOW_ID_REGEX = re.compile(r"(?<=\[).*(?=\])")

# TODO: hotkey to open clipped link in chosen window


class WindowIdRegexNoMatch(Exception):
    pass


class WindowSelectionPrompt(Prompt):
    _action_menu_type = ActionMenu

    @mods.preview(
        "source ~/.zshforchrome 2>/dev/null && echo {} | get_chrome_id | read -r window_id && brotab query -windowId $window_id | brotab_format_better_line",
        70,
    )
    # ggrep -Po "(?<=\\.)\\d*" for BroTab IDs (from `brotab windows`) instead of get_chrome_id
    @mods.exit_round_on_no_selection
    @Options().defaults
    def __call__(self, options: Options = Options()) -> Result:
        return run_fzf_prompt(
            choices=sorted(shell_command("chrome-cli list windows").split("\n"), key=lambda x: x.split("]")[1]),
            fzf_options=self._options + options,
        )


class ChromeWindowManager:
    def __init__(self) -> None:
        self.select_window = WindowSelectionPrompt()

    def run(self, options: Options = Options()):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        # TODO: maybe there's no need to have options
        window = self.select_window()[0]
        # window = self._window_prompt()
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

    def extract_window_id(self, line: str) -> str:
        if match := WINDOW_ID_REGEX.search(line):
            return match[0]
        else:
            raise WindowIdRegexNoMatch(f"No match for '{line}'")

    def focus_window(self, window_id: str):
        active_tab_id = shell_command(f"brotab active | grep {window_id} | awk '{{ print $1 }}'")
        shell_command(f'open -a "Google Chrome" && brotab activate {active_tab_id} --focused')
        time.sleep(1.2)


if __name__ == "__main__":
    cwm = ChromeWindowManager()
    cwm.run_in_loop()
