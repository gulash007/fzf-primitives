import re
import time

from thingies import shell_command

from .core import mods
from .core.ActionMenu import ActionMenu
from .core.BasicLoop import BasicLoop
from .core import DefaultPrompt as default_prompt
from .core.MyFzfPrompt import Result
from .core.options import Options
from .core.Prompt import Prompt

WINDOW_ID_REGEX = re.compile(r"(?<=\[).*(?=\])")

# TODO: hotkey to open clipped link in chosen window

action_menu = ActionMenu()


class WindowIdRegexNoMatch(Exception):
    pass


@mods.preview(
    "source ~/.zshforchrome 2>/dev/null && echo {} | get_chrome_id | read -r window_id && brotab query -windowId $window_id | brotab_format_better_line",
    70,
)
# ggrep -Po "(?<=\\.)\\d*" for BroTab IDs (from `brotab windows`) instead of get_chrome_id
def run_window_selection_prompt(options: Options = Options()) -> Result:
    result = default_prompt.run(
        choices=sorted(shell_command("chrome-cli list windows").split("\n"), key=lambda x: x.split("]")[1]),
        options=options,
    )
    if isinstance(result, Prompt):
        raise TypeError(f"{result} should be of type Result")
    return result


class ChromeWindowManager(BasicLoop):
    def __init__(self) -> None:
        pass

    def run(self):
        """Runs one round of the application until end state. Loop should be implemented externally"""
        window = run_window_selection_prompt()[0]
        # window = self._window_prompt()
        window_id = self.extract_window_id(window)
        self.focus_window(window_id)

    def extract_window_id(self, line: str) -> str:
        if not (match := WINDOW_ID_REGEX.search(line)):
            raise WindowIdRegexNoMatch(f"No match for '{line}'")
        return match[0]

    def focus_window(self, window_id: str):
        active_tab_id = shell_command(f"brotab active | grep {window_id} | awk '{{ print $1 }}'")
        shell_command(f'open -a "Google Chrome" && brotab activate {active_tab_id} --focused')
        time.sleep(1.2)


if __name__ == "__main__":
    cwm = ChromeWindowManager()
    cwm.run_in_loop()
