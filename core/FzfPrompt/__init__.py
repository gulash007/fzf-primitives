from __future__ import annotations

import os
import subprocess
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
    ServerEndpoint,
    make_server_call,
)
from .shell import MoreInformativeCalledProcessError

__all__ = [
    "run_fzf_prompt",
    "PromptData",
    "Result",
    "Binding",
    "BindingConflict",
    "Action",
    "ConflictResolution",
    "ShellCommand",
    "ServerEndpoint",
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


FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable
# Inspired by https://github.com/nk412/pyfzf
def run_fzf_prompt[T, S](prompt_data: PromptData[T, S], *, executable_path=None) -> Result[T]:
    logger = Logger.get_logger()

    prompt_data.run_initial_setup()
    server = prompt_data.server
    server.start()
    server.setup_finished.wait()
    env = os.environ.copy()
    env[SOCKET_NUMBER_ENV_VAR] = str(server.socket_number)
    env[MAKE_SERVER_CALL_ENV_VAR_NAME] = make_server_call.__file__
    prompt_data.run_vars.update({"env": env, "executable_path": executable_path})

    # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
    try:
        options = prompt_data.options
        logger.debug(f"Running fzf with options:\n{options.pretty()}")
        subprocess.run(
            [executable_path or "fzf", *options],
            shell=False,
            input=prompt_data.choices_string.encode(),
            check=True,
            env=env,
            stdout=subprocess.DEVNULL,
        )
    except FileNotFoundError as err:
        if executable_path:
            raise FzfExecutionError(f"Error running 'fzf' with executable_path: {executable_path}") from err
        raise FzfExecutionError(
            f"Error running 'fzf' command. Are you sure it's installed and on PATH? ({FZF_URL})"
        ) from err
    except subprocess.CalledProcessError as err:
        # 130 means aborted, 1 means accepted with no selection
        if err.returncode not in (130, 1):
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


class FzfExecutionError(Exception):
    pass
