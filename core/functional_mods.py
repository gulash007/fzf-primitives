from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from pyfzf import FzfPrompt
from core.exceptions import ExitLoop, ExitRound

from core.options import Options

OBSIDIAN_REPO_PATH = Path("/Users/honza/Documents/HOLLY")
DAILY_FOLDER_REL_PATH = Path("ALFRED/Personal/Daily")
DAILY_FOLDER_PATH = OBSIDIAN_REPO_PATH.joinpath(DAILY_FOLDER_REL_PATH)
WEEKLY_FOLDER_REL_PATH = Path("ALFRED/Personal/Weekly")
WEEKLY_FOLDER_PATH = OBSIDIAN_REPO_PATH.joinpath(WEEKLY_FOLDER_REL_PATH)


class Prompt(FzfPrompt):
    def prompt(self, choices: list[str] = None, fzf_options: Options = Options(), delimiter: str = "\n"):
        return super().prompt(choices, str(fzf_options), delimiter)


def exit_round_on_no_selection(func: Callable[..., list]):
    def exiting_round_on_no_selection(choices, fzf_options: Options = Options(), delimiter="\n"):
        if not (output := func(choices, fzf_options, delimiter)):
            raise ExitRound  # TODO: custom message (decorator factory)
        return output

    return exiting_round_on_no_selection


def f(path: Path, sorting_key: Callable = None) -> list[Path]:
    return sorted((p.relative_to(DAILY_FOLDER_PATH) for p in path.iterdir()), key=sorting_key)


def g(choices: list[Path]) -> Path:
    key, choice = exit_round_on_no_selection(Prompt().prompt)(choices=choices, fzf_options=Options().expect("enter"))
    return Path(choice)


if __name__ == "__main__":
    print(g(f(DAILY_FOLDER_PATH)))

HOLLY_LOCATION = Path("/Users/honza/Documents/HOLLY")


class FilesPrompt:
    def __call__(self, directory: Path):
        pass


class LinesPrompt:
    def __call__(self, file_path: Path):
        pass


@dataclass
class FunctionalObsidianBrowser:
    repo_location: Path = HOLLY_LOCATION

    def run(self):
        while True:
            try:
                files_prompt = self._files_prompt(self.repo_location)
                lines_prompt = self._lines_prompt(files_prompt)
                self._do_something_with(lines_prompt.result())
            except ExitLoop:
                print("Exiting loop")
                break
