import os
import time
from pathlib import Path
import traceback
from typing import Self

from pydantic import BaseModel, parse_file_as


from thingies import shell_command

from ..core import BasePrompt, mods
from ..core.BasicLoop import BasicLoop
from ..core.FzfPrompt.Prompt import Result
from ..core.FzfPrompt.PromptData import PromptData


# TODO: hotkey to open clipped link in chosen window
# TODO: Save sessions (or at least window names)
# TODO: Convenient window naming


class WindowIdRegexNoMatch(Exception):
    pass


STORED_WINDOWS_PATH = Path(__file__).parent.joinpath("windows.json")


class Window(BaseModel):
    id: str
    active_tab_title: str
    name: str | None = None

    def update(self, other: Self):
        self.name = other.name

    def __str__(self) -> str:
        return f"{self.id}  {self.name or self.active_tab_title}"

    @classmethod
    def from_brotab(cls, brotab_line: str) -> Self:
        active_tab_id, active_tab_title = brotab_line.split(maxsplit=1)
        return cls(id=active_tab_id.rsplit(".", maxsplit=1)[0], active_tab_title=active_tab_title)


class Windows(BaseModel):
    windows: dict[str, Window]

    # TODO: handle file not existing or being corrupted
    @classmethod
    def get_saved_windows(cls) -> Self:
        try:
            return parse_file_as(cls, STORED_WINDOWS_PATH)
        except Exception:
            print(traceback.format_exc())
            return Windows(windows={})

    @classmethod
    def from_list_of_windows(cls, windows: list[Window]):
        return cls(windows={window.id: window for window in windows})

    def save(self):
        Path(os.path.dirname(STORED_WINDOWS_PATH)).mkdir(parents=True, exist_ok=True)
        with open(STORED_WINDOWS_PATH, "w", encoding="utf-8") as f:
            f.write(self.json(indent=2))

    def update(self, other_windows: Self):
        for window in other_windows.windows.values():
            if window.id in self.windows:
                self.windows[window.id].update(window)


def get_windows() -> Windows:
    current_windows = Windows.from_list_of_windows(
        [Window.from_brotab(brotab_line) for brotab_line in shell_command("brotab query +active").split("\n")]
    )
    saved_windows = Windows.get_saved_windows()
    current_windows.update(saved_windows)
    current_windows.save()
    return current_windows


def focus_window(window_id: str):
    active_tab_id = shell_command(f"brotab active | grep {window_id} | awk '{{ print $1 }}'")
    shell_command(f'open -a "Google Chrome" && brotab activate {active_tab_id} --focused')
    time.sleep(0.3)


@mods.exit_round_on_no_selection()
@mods.preview.custom(
    "List tabs",
    "source ~/.zshforchrome 2>/dev/null && echo {} | awk '{ print $1 }' | read -r window_id && brotab query -windowId ${window_id:2} | brotab_format_better_line",
    "ctrl-y",
)
def run_window_selection_prompt(prompt_data: PromptData) -> Result:
    return BasePrompt.run(prompt_data=prompt_data)


def run():
    """Runs one round of the application until end state. Loop should be implemented externally"""
    windows = get_windows()
    window_mapping = {str(window): window for window in windows.windows.values()}
    window = window_mapping[
        run_window_selection_prompt(
            PromptData(
                choices=sorted(window_mapping.values(), key=lambda x: (not x.name, str(x.name), x.active_tab_title))
            )
        )[0]
    ]
    focus_window(window.id)


if __name__ == "__main__":
    BasicLoop(run).run_in_loop()
