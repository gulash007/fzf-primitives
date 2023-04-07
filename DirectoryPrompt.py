from pathlib import Path
from typing import Callable
from core.ActionMenu import ActionMenu, as_action
from core.BasicLoop import BasicRecursiveLoop
from core.MyFzfPrompt import Result, run_fzf_prompt
from core.Prompt import Prompt
from core.options import HOTKEY, Options
from thingies import SortingKey, shell_command
from core import mods


class DirectoryActionMenu(ActionMenu):
    # @action(HOTKEY.ctrl_o)
    # def open_file(self, result: Result):
    #     shell_command('execute(file_name={} && note_name=${file_name%.md} && note_name=$(echo $note_name | jq -R -r @uri) && open "obsidian://open?vault=HOLLY&file=${note_name%.md}")')
    pass


class DirectoryPrompt(Prompt):
    _action_menu_type = DirectoryActionMenu
    action_menu: DirectoryActionMenu

    def __init__(self, dirpath: Path, sorting_key: Callable = SortingKey().alphabetically) -> None:
        super().__init__()
        self.dirpath = dirpath
        self._sorting_key = sorting_key
        self._options = self._options.ansi.multiselect

    # @mods.hotkey_python(HOTKEY.ctrl_b, )
    def __call__(self) -> Result:
        files = sorted(
            (Path(line) for line in shell_command(f"find {self.dirpath} -maxdepth 1").splitlines()),
            key=self._sorting_key,
        )
        return run_fzf_prompt(choices=files, fzf_options=self._options)


if __name__ == "__main__":
    REPO_LOCATION = Path("/Users/honza/Documents/HOLLY")
    d = DirectoryPrompt(REPO_LOCATION, sorting_key=SortingKey().directory_first().alphabetically())
    basic_loop = BasicRecursiveLoop(d)

    print(basic_loop.run())
