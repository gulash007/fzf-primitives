from __future__ import annotations

import os
import sys
from pathlib import Path

import loguru
from loguru import logger
from pyfzf import FzfPrompt
from stringcolor import cs

from core import mods
from core.exceptions import ExitLoop, ExitRound
from core.constants import HOTKEY

LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{process.id}</cyan> - <cyan>{process.name}</cyan> - <white>{thread.name}</white> - <white>{function}</white>:<white>{line}</white>: <level>{message} - {extra}</level>"
logger.remove()
logger.add(sys.stderr, level="DEBUG", format=LOG_FORMAT, enqueue=True, colorize=True)
# logger.add(sys.stderr, level="ERROR", format=LOG_FORMAT, enqueue=True, serialize=True)
# LOG_PATH = Path(f"{os.getcwd()}/_logs/some.log")
# logger.add(
#     LOG_PATH,
#     level="DEBUG",
#     format=LOG_FORMAT,
#     enqueue=True,
#     serialize=True,
#     colorize=True,
#     rotation="30 seconds",
#     retention="10 MB",
# )


def get_logger(name: str) -> loguru.Logger:
    return logger.bind(context=name)


logger = get_logger(__name__)


def colorized(line: str) -> str:
    return str(cs(line, "orchid"))


class FileBrowser:
    def __init__(self, starting_folder: Path = Path.home()) -> None:
        self.folder = starting_folder
        self._history = []

    def run_in_loop(self):
        while True:
            try:
                key, path = self.browse_files()
                if key == HOTKEY.ctrl_a:
                    self.go_back()
                if key == HOTKEY.enter:
                    self.move(Path(path))
            except ExitRound:
                continue
            except ExitLoop:
                break
            except Exception as e:
                logger.exception(e)
                self.go_back()
                continue

    def move(self, path: Path):
        if path.is_dir():
            self._history.append(self.folder)
            self.folder = path
        else:
            raise ExitRound("Path is not a directory")

    @mods.add_options("--expect=enter,ctrl-a")
    @mods.preview(
        "source ~/.zsh_aliases && ll {}"
    )  # show files in a folder or preview a file if it has the right extension
    @mods.ansi
    @mods.defaults
    @mods.exit_round_on_no_selection
    @mods.exit_loop_hotkey
    def browse_files(self, options=""):
        return FzfPrompt().prompt(
            choices=[
                colorized(str(p)) if p.is_dir() else p
                for p in sorted(self.folder.iterdir(), key=lambda x: (not x.is_dir(), str(x)))
            ],
            fzf_options=options,
        )

    def go_back(self):
        previous_folder = self._history.pop()
        logger.warning(f"Returning back to {self.folder}")
        self.folder = previous_folder


class FileBrowser:
    def __init__(self, starting_folder: Path = Path.home()) -> None:
        self._folder = starting_folder

    def run(self):
        # create prompt
        # based on key in key, output pair perform an action (may change .folder)
        while True:
            self._folder = self._prompt.run()


class BrowseFilesPrompt:
    pass


if __name__ == "__main__":
    fb = FileBrowser()
    fb.run_in_loop()
