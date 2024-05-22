from typing import get_args

import pygments
from pygments.formatters import Terminal256Formatter
from pygments.lexers import JsonLexer

from ..... import prompt as pr
from .....FzfPrompt import PromptData
from .....FzfPrompt.server import ServerEndpoint
from .....FzfPrompt.server.make_server_call import make_server_call
from .inspection import Inspectable


def get_inspector_prompt(inspected: PromptData | int):
    """inspected can be a PromptData object or a backend port of remote prompt"""
    prompt = pr.Prompt[Inspectable, None](list(get_args(Inspectable)), use_basic_hotkeys=False)
    if isinstance(inspected, PromptData):
        prompt.mod.preview().custom(
            "Inspections",
            lambda pd: pygments.highlight(
                inspected.server.endpoints["INSPECT"].function(
                    inspected,
                    inspection_view_specs={line: 1 for line in pd.current_choices},
                ),
                lexer=JsonLexer(),
                formatter=Terminal256Formatter(),
            ),
            window_size="85%",
        )

    else:
        prompt.mod.preview().custom(
            "Inspections",
            lambda pd: pygments.highlight(
                make_server_call(
                    inspected, "INSPECT", None, inspection_view_specs={line: 1 for line in pd.current_choices}
                ),
                lexer=JsonLexer(),
                formatter=Terminal256Formatter(),
            ),
            window_size="85%",
        )

        def change_port(prompt_data: PromptData, _port: str):
            if not _port:
                _port = input("Enter port: ")
            if _port.isdigit():
                prompt_data.obj = int(_port)

        prompt.mod.on_hotkey().CTRL_B.run_function("Change port", change_port, "refresh-preview")

        prompt.mod._mods.append(lambda pd: pd.server.add_endpoint(ServerEndpoint(change_port, "CHANGE_INSPECTED_PORT")))

    prompt.mod.options.multiselect

    prompt.mod.on_hotkey().CTRL_C.run_function(
        "Clip backend and control port", lambda pd: copy_backend_and_control_port(pd.server.port, pd.control_port)
    )
    prompt.mod.on_hotkey().CTRL_Y.auto_repeat_run("refresh", "refresh-preview", repeat_interval=0.1)
    prompt.mod.on_hotkey().ESC.refresh_preview
    prompt.mod.on_hotkey().ENTER.abort  # TODO: do something
    prompt.mod.on_hotkey().CTRL_Q.abort
    prompt.mod.on_hotkey().CTRL_ALT_H.show_bindings_help_in_preview
    prompt.mod.on_hotkey().CTRL_ALT_C.run_function(
        "Copy command to run inspector externally",
        lambda pd: copy_command_to_run_inspector_externally(
            inspected if isinstance(inspected, int) else inspected.server.port
        ),
        silent=True,
    ).accept

    prompt.mod.expose_inspector("ctrl-alt-i")

    return prompt


def copy_backend_and_control_port(backend_port: int, control_port: int):
    import pyperclip

    pyperclip.copy(f"{backend_port}, {control_port}")


def copy_command_to_run_inspector_externally(port: int):
    import pyperclip

    pyperclip.copy(f"python -m fzf_primitives.extra.inspector {port}")
