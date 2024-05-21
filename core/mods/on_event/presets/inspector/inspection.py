import json
from typing import Any, Callable, Literal

from ......config import Config
from .....FzfPrompt import PromptData
from .....FzfPrompt.server import ServerEndpoint

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
    "control_port",
]

# TODO: Use depth and add hotkeys to change it
INSPECTORS: dict[Inspectable, Callable[[PromptData, int], Any]] = {
    "action_menu": lambda pd, depth: {
        "bindings": pd.action_menu.bindings,
    },
    "server": lambda pd, depth: {
        "endpoints": {k: str(v) for k, v in pd.server.endpoints.items()},
        "port": pd.server.port,
        "setup_finished": pd.server.setup_finished,
        "should_close": pd.server.should_close,
    },
    "previewer": lambda pd, depth: {
        "current_preview": pd.previewer.current_preview.id,
        "previews": [p.id for p in pd.previewer.previews],
    },
    "automator": lambda pd, depth: "automator inspection function not implemented yet",
    "options": lambda pd, depth: {
        "options": pd.options.options,
    },
    "config": lambda pd, depth: {k: v for k, v in Config.__dict__.items() if not k.startswith("__")},
    "obj": lambda pd, depth: pd.obj,
    "choices": lambda pd, depth: pd.choices,
    "current_state": lambda pd, depth: {
        **pd.current_state.__dict__,
        "current single choice": pd.current_single_choice,
        "current choices": pd.current_choices,
        "stage": pd.stage,
    },
    "run_vars": lambda pd, depth: pd.run_vars,
    "control_port": lambda pd, depth: pd.control_port,
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


INSPECTION_ENDPOINT = ServerEndpoint(show_inspectables, "INSPECT")
