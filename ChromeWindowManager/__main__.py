import difflib
import os
import time
import traceback
from pathlib import Path
from typing import Self

from pydantic import BaseModel, parse_file_as
from thingies import shell_command

from ..core import DefaultPrompt, mods
from ..core import BasicLoop
from ..core.FzfPrompt.exceptions import ExitRound
from ..core.FzfPrompt.Prompt import ActionMenu, PromptData, Result, ShellCommand, PromptEndingAction
from ..core.monitoring.Logger import get_logger

logger = get_logger()


# TODO: hotkey to open clipped link in chosen window
# TODO: Save sessions (or at least window names)
# TODO: Convenient window naming (ctrl-n hotkey?)
# TODO: Highlight active window
# TODO: Highlight active tab
# TODO: open windows.json in given window


class WindowIdRegexNoMatch(Exception):
    pass


STORED_WINDOWS_PATH = Path(__file__).parent.joinpath("windows.json")


class Tab(BaseModel):
    id: str
    title: str
    url: str

    @property
    def window_id(self) -> str:
        return self.id.rsplit(".", maxsplit=1)[0]

    @classmethod
    def from_brotab_line(cls, line: str) -> Self:
        """Line generated by `brotab list` or `brotab query +active` commands"""
        tab_id, title, url = line.split("\t")
        return cls(id=tab_id, title=title, url=url)


class Window(BaseModel):
    id: str
    active_tab: Tab
    tabs: list[Tab]
    name: str | None = None

    def update(self, other: Self):
        self.name = other.name

    def __str__(self) -> str:
        return f"{self.id}  {self.name or self.active_tab.title}"

    @classmethod
    def from_tab(cls, tab: Tab) -> Self:
        return cls(id=tab.window_id, active_tab=tab, tabs=[tab])

    def is_similar_to(self, other: Self) -> bool:
        """For each tab find the most similar tabs"""
        matches = [
            max(difflib.SequenceMatcher(None, other_tab.url, tab.url).ratio() for tab in self.tabs)
            for other_tab in other.tabs
        ]
        similarity_score = sum(matches) / len(matches)
        if similarity_score > 0.9:
            return True
        elif similarity_score > 0.4:
            return run_similarity_prompt(self, other)
        else:
            return False


def run_similarity_prompt(window: Window, other_window: Window) -> bool:
    return False


class Windows(BaseModel):
    windows: dict[str, Window]  # key is window.id

    @classmethod
    def get_current_windows(cls) -> Self:
        return cls.from_brotab()

    @classmethod
    def get_saved_windows(cls) -> Self:
        try:
            return parse_file_as(cls, STORED_WINDOWS_PATH)
        except Exception:
            print(traceback.format_exc())
            return Windows(windows={})

    def save(self):
        Path(os.path.dirname(STORED_WINDOWS_PATH)).mkdir(parents=True, exist_ok=True)
        with open(STORED_WINDOWS_PATH, "w", encoding="utf-8") as f:
            f.write(self.json(indent=2))

    def update(self, other_windows: Self):
        for other_window in other_windows.windows.values():
            if other_window.name is None:
                continue
            if other_window.id in self.windows:
                self.windows[other_window.id].update(other_window)
                continue
            for window in self.windows.values():
                if window.is_similar_to(other_window):
                    window.update(other_window)

    @classmethod
    def from_brotab(cls) -> Self:
        tabs = [Tab.from_brotab_line(line) for line in shell_command("brotab list").splitlines()]
        active_tabs = [Tab.from_brotab_line(line) for line in shell_command("brotab query +active").splitlines()]
        windows = {}
        for tab in tabs:
            if tab.window_id not in windows:
                windows[tab.window_id] = Window.from_tab(tab)
            else:
                windows[tab.window_id].tabs.append(tab)
                if tab in active_tabs:
                    windows[tab.window_id].active_tab = tab

        return cls(windows=windows)


def get_windows() -> Windows:
    current_windows = Windows.get_current_windows()
    saved_windows = Windows.get_saved_windows()
    current_windows.update(saved_windows)
    current_windows.save()
    return current_windows


def focus_window(window_id: str):
    active_tab_id = shell_command(f"brotab active | grep {window_id} | awk '{{ print $1 }}'")
    shell_command(f'open -a "Google Chrome" && brotab activate {active_tab_id} --focused')
    time.sleep(0.3)


class ActionMenuWithWindows(ActionMenu):
    def __init__(self, windows: Windows) -> None:
        self.windows = windows
        super().__init__()


def close_window(prompt_data: PromptData):
    window_id = prompt_data.result[0].split()[0]
    window = prompt_data.action_menu.windows.windows[window_id]
    shell_command(f"brotab close {' '.join(tab.id for tab in window.tabs)}")
    raise ExitRound


@mods.on_event("ctrl-g").run("Open windows.json", ShellCommand(f"code-insiders '{STORED_WINDOWS_PATH}'"))
@mods.preview("ctrl-y")(
    "List tabs",
    "source ~/.zshforchrome 2>/dev/null && echo {} | awk '{ print $1 }' | read -r window_id && brotab query -windowId ${window_id:2} | brotab_format_better_line",
)
@mods.on_event("ctrl-w").run("Close window", PromptEndingAction("accept", close_window))
@mods.on_event("ctrl-o").run("Open windows.json", ShellCommand(f"code-insiders '{STORED_WINDOWS_PATH}'"))
def run_window_selection_prompt(prompt_data: PromptData) -> Result:
    return DefaultPrompt.run(prompt_data=prompt_data)


def run():
    windows = get_windows()
    window_mapping = {str(window): window for window in windows.windows.values()}
    window = window_mapping[
        run_window_selection_prompt(
            PromptData(
                choices=sorted(window_mapping.values(), key=lambda x: (not x.name, str(x.name), x.active_tab.title)),
                action_menu=ActionMenuWithWindows(windows),
            )
        )[0]
    ]
    focus_window(window.id)


if __name__ == "__main__":
    BasicLoop.run_in_loop(run)
