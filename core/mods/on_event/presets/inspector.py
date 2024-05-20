import json
from typing import Any, Callable, Literal, get_args

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


def get_inspector_prompt(inspected: PromptData | int):
    if isinstance(inspected, PromptData):
        prompt = pr.Prompt[Inspectable, PromptData](list(get_args(Inspectable)), obj=inspected, use_basic_hotkeys=False)
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

    else:
        port = inspected
        prompt = pr.Prompt[Inspectable, int](list(get_args(Inspectable)), obj=port, use_basic_hotkeys=False)
        prompt.mod.preview().custom(
            "Inspections",
            lambda pd: pygments.highlight(
                make_server_call(
                    pd.obj, "INSPECT", None, inspection_view_specs={line: 1 for line in pd.current_choices}
                ),
                lexer=JsonLexer(),
                formatter=Terminal256Formatter(),
            ),
            window_size="85%",
        )

        def change_port(prompt_data: PromptData, port: str):
            if not port:
                port = input("Enter port: ")
            prompt_data.obj = int(port)

        prompt.mod.on_hotkey().CTRL_B.run_function("Change port", change_port, "refresh-preview")

    prompt.mod.options.multiselect

    prompt.mod.on_hotkey().CTRL_Y.auto_repeat_run("refresh", "refresh-preview", repeat_interval=0.1)
    prompt.mod.on_hotkey().ESC.refresh_preview
    prompt.mod.on_hotkey().CTRL_Q.quit
    prompt.mod.on_hotkey().CTRL_ALT_H.show_bindings_help_in_preview
    prompt.mod.on_hotkey().CTRL_ALT_C.run_function(
        "Copy command to run inspector externally",
        lambda pd: copy_command_to_run_inspector_externally(
            inspected if isinstance(inspected, int) else inspected.server.socket_number
        ),
        silent=True,
    ).accept

    return prompt


def copy_command_to_run_inspector_externally(port: int):
    import pyperclip

    pyperclip.copy(f"python -m fzf_primitives.extra.inspector {port}")
