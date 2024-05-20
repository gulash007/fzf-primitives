import json
from typing import Any, Callable, Literal, get_args, overload

import pygments
from pygments.formatters import Terminal256Formatter
from pygments.lexers import JsonLexer

from .....config import Config
from .....core import prompt as pr
from .....core.FzfPrompt.server.make_server_call import make_server_call
from ....FzfPrompt import PromptData

Inspectable = Literal[
    "action_menu",
    "server",
    "previewer",
    "automator",
    "options",
    "config",
    "obj",
    "choices",
    "current_state",
    "run_vars",
]

# TODO: Use depth and add hotkeys to change it
INSPECTORS: dict[Inspectable, Callable[[PromptData, int], Any]] = {
    "action_menu": lambda pd, depth: {
        "bindings": pd.action_menu.bindings,
    },
    "server": lambda pd, depth: {
        "server_calls": {k: str(v) for k, v in pd.server.server_calls.items()},
    },
    "previewer": lambda pd, depth: {
        "current_preview": pd.previewer.current_preview.id,
        "previews": [p.id for p in pd.previewer.previews],
    },
    "automator": lambda pd, depth: "automator inspection function not implemented yet",
    "options": lambda pd, depth: {
        "options": pd.options.options,
    },
    "config": lambda pd, depth: Config,
    "obj": lambda pd, depth: pd.obj,
    "choices": lambda pd, depth: pd.choices,
    "current_state": lambda pd, depth: {
        **pd.current_state.__dict__,
        "current single choice": pd.current_single_choice,
        "current choices": pd.current_choices,
    },
    "run_vars": lambda pd, depth: pd.run_vars,
}


# the ints represent depths of view
def show_inspectables(prompt_data: PromptData, inspection_view_specs: dict[Inspectable, int]) -> str:
    outputs = {key: INSPECTORS[key](prompt_data, value) for key, value in inspection_view_specs.items()}
    return json.dumps(
        outputs,
        indent=2,
        sort_keys=False,
        default=lambda obj: getattr(obj, "__name__", None) or getattr(obj, "__dict__", None) or str(obj),
    )


@overload
def get_inspector_prompt(*, inspected_prompt_data: PromptData): ...
@overload
def get_inspector_prompt(*, port: int): ...
def get_inspector_prompt(*, inspected_prompt_data: PromptData | None = None, port: int | None = None):
    if inspected_prompt_data:
        prompt = pr.Prompt[Inspectable, PromptData](list(get_args(Inspectable)), obj=inspected_prompt_data)
        prompt.mod.preview().custom(
            "Inspections",
            lambda pd: pygments.highlight(
                pd.obj.server.server_calls["INSPECT"].function(
                    pd.obj,
                    inspection_view_specs={line: 1 for line in pd.current_choices},
                ),
                lexer=JsonLexer(),
                formatter=Terminal256Formatter(),
            ),
            window_size="85%",
        )

    elif port:
        prompt = pr.Prompt[Inspectable, None](list(get_args(Inspectable)))
        prompt.mod.preview().custom(
            "Inspections",
            lambda pd: pygments.highlight(
                make_server_call(
                    port, "INSPECT", "preview", None, inspection_view_specs={line: 1 for line in pd.current_choices}
                ),
                lexer=JsonLexer(),
                formatter=Terminal256Formatter(),
            ),
            window_size="85%",
        )

    prompt.mod.options.multiselect

    prompt.mod.on_hotkey().CTRL_Y.auto_repeat_run("refresh", "refresh-preview", repeat_interval=0.25)
    return prompt
