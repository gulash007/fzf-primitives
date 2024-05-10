from __future__ import annotations

import os
import shlex
import subprocess
from shutil import which
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .prompt_data import PromptData
    from .server import PromptEndingAction, ServerCall
from ..monitoring import Logger
from .action_menu.ActionMenu import BindingConflict, ConflictResolution
from .action_menu.binding import Binding
from .action_menu.parametrized_actions import Action, ShellCommand
from .action_menu.transform import ActionsBuilder, Transform
from .exceptions import Quitting
from .previewer import (
    Preview,
    PreviewChangePreProcessor,
    PreviewFunction,
    PreviewMutationArgs,
    PreviewMutator,
    PreviewStyleMutationArgs,
)
from .prompt_data import ChoicesAndLinesMismatch, PromptData, Result
from .server import (
    MAKE_SERVER_CALL_ENV_VAR_NAME,
    SOCKET_NUMBER_ENV_VAR,
    EndStatus,
    PostProcessor,
    PromptEndingAction,
    ServerCall,
    ServerCallFunction,
)
from .shell import SHELL_SCRIPTS, MoreInformativeCalledProcessError

__all__ = [
    "run_fzf_prompt",
    "PromptData",
    "Result",
    "Binding",
    "BindingConflict",
    "Action",
    "ConflictResolution",
    "ShellCommand",
    "ServerCall",
    "ServerCallFunction",
    "PromptEndingAction",
    "PostProcessor",
    "EndStatus",
    "Preview",
    "PreviewFunction",
    "PreviewChangePreProcessor",
    "PreviewMutator",
    "PreviewMutationArgs",
    "PreviewStyleMutationArgs",
    "Transform",
    "ActionsBuilder",
    "ChoicesAndLinesMismatch",
]

# Black magic layer
# - Among other things, ensures communication between Python script and running fzf process


FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable
# Inspired by https://github.com/nk412/pyfzf
def run_fzf_prompt[T, S](prompt_data: PromptData[T, S], *, executable_path=None) -> Result[T]:
    logger = Logger.get_logger()
    if executable_path:
        pass
    elif which("fzf"):
        executable_path = "fzf"
    else:
        raise SystemError(f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")

    if prompt_data.should_run_automator:
        from ..FzfPrompt.automator import Automator

        automator = Automator()
        automator.prepare(prompt_data)
        automator.start()

    server = prompt_data.server
    for binding in prompt_data.action_menu.bindings.values():
        server.add_server_calls(binding)
    server.start()
    server.setup_finished.wait()
    env = os.environ.copy()
    env[SOCKET_NUMBER_ENV_VAR] = str(server.socket_number)
    env[MAKE_SERVER_CALL_ENV_VAR_NAME] = str(SHELL_SCRIPTS.make_server_call)

    # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
    try:
        options = prompt_data.resolve_options()
        options.listen()  # TODO: For getting fzf JSON (contain this somewhere)
        logger.debug(f"Running fzf with options:\n{options.pretty()}")
        subprocess.run(
            [executable_path, *shlex.split(str(options))],
            shell=False,
            input=prompt_data.choices_string.encode(),
            check=True,
            env=env,
        )
    except subprocess.CalledProcessError as err:
        # 130 means aborted or unassigned hotkey was pressed
        if err.returncode != 130:
            raise MoreInformativeCalledProcessError(err) from None
    finally:
        server.should_close.set()
    server.join()
    if not prompt_data.finished:
        # TODO: This may be explicitly allowed in the future (need to test when it's not)
        raise RuntimeError("Prompt not finished (you aborted prompt without finishing PromptData)")
    if prompt_data.result.end_status == "quit":
        raise Quitting(f"Exiting app with\n{prompt_data.result}", prompt_data.result)
    prompt_data.apply_post_processors()
    return prompt_data.result
