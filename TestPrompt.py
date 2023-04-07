from pathlib import Path
from typing import Iterable

from .core.MyFzfPrompt import Result

from .core.options import Options
from .core import mods
from .core.Prompt import Prompt
from .core.previews import PREVIEW
from .core.actions.preview_file import preview_file

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")


class TestPrompt(Prompt):
    _instance_created = False

    @Options().multiselect
    @mods.preview(PREVIEW.basic)
    def run(self, *, choices: Iterable = None, options: Options = Options()) -> Result | Prompt:
        return super().run(choices=choices, options=options)


test_prompt = TestPrompt()

files = test_prompt.run(choices=["VS Code TODO.md", "Obsidian TODO.md"])


print(preview_file("", list(files), directory=str(HOLLY_VAULT)))
