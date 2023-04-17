from pathlib import Path
from typing import Iterable

from ..core.MyFzfPrompt import Result

from ..core.options import Options
from ..core import mods
from ..core import DefaultPrompt
from ..core import Prompt
from ..core.previews import PREVIEW
from ..core.actions.view_file import view_file
from ..core.intercom.PromptData import PromptData

HOLLY_VAULT = Path("/Users/honza/Documents/HOLLY")

# TEST ALL KINDS OF STUFF


@mods.preview(PREVIEW.basic)
def run(prompt_data: PromptData, options: Options = Options(), choices=None):
    choices = choices or []
    return Prompt.run(choices, prompt_data, options.multiselect)


UPDATE_COMMAND = "execute-silent(/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/.env/bin/python3.11 -m fzf_primitives.experimental.core.intercom.commands.update_prompt_data %s {q} {+})"

if __name__ == "__main__":
    # prompt_data = PromptData.load("2023-04-16T13:43:48.902980")
    # print(prompt_data)
    # preview = prompt_data.get_preview_output("basic")
    # print(preview)
    from datetime import datetime, date, timedelta

    pd = PromptData(id=datetime.now().isoformat())
    run(
        pd,
        options=Options(f"--bind 'focus:{UPDATE_COMMAND}' --bind 'change:{UPDATE_COMMAND}'" % (pd.id, pd.id)),
        choices=[1, 2, 3],
    )
