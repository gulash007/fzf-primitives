import json
from typing import Any, Callable, Literal, get_args

import pygments
from pygments.formatters import Terminal256Formatter
from pygments.lexers import JsonLexer

from .....core import prompt as pr
from ....FzfPrompt import PromptData

# TODO: add automator after you make it a part of PromptData
# TODO: Make everything that determines the prompt a part of PromptData
Inspectable = Literal["action_menu", "server", "previewer", "automator", "options", "obj", "choices", "current_state"]

INSPECTORS: dict[Inspectable, Callable[[PromptData], Any]] = {
    "action_menu": lambda pd: {
        "bindings": pd.action_menu.bindings,
    },
    "server": lambda pd: {
        "server_calls": {k: str(v) for k, v in pd.server.server_calls.items()},
    },
    "previewer": lambda pd: {
        "current_preview": pd.previewer.current_preview.id,
        "previews": [p.id for p in pd.previewer.previews],
    },
    "automator": lambda pd: "automator inspection function not implemented yet",
    "options": lambda pd: {
        "options": pd.options.options,
    },
    "obj": lambda pd: pd.obj,
    "choices": lambda pd: pd.choices,
    "current_state": lambda pd: {
        **pd.current_state.__dict__,
        "current single choice": pd.current_single_choice,
        "current choices": pd.current_choices,
    },
}


def show_inspectables(prompt_data: PromptData) -> str:
    outputs = {line: INSPECTORS[line](prompt_data) for line in prompt_data.current_choices}
    json_output = json.dumps(
        outputs,
        indent=2,
        sort_keys=False,
        default=lambda obj: getattr(obj, "__name__", None) or getattr(obj, "__dict__", None) or str(obj),
    )
    # prompt_data.obj.update({str(datetime.now()): "+".join(prompt_data.current_state.lines)})
    return pygments.highlight(json_output, lexer=JsonLexer(), formatter=Terminal256Formatter())


def get_inspector_prompt():
    prompt = pr.Prompt(list(get_args(Inspectable)))
    prompt.mod.options.multiselect

    prompt.mod.preview().custom("Inspections", show_inspectables, window_size="85%")

    prompt.mod.on_hotkey().CTRL_Y.auto_repeat_run("refresh", "refresh-preview", repeat_interval=0.25)
    return prompt
