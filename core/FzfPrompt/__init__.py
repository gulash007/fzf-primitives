from __future__ import annotations

import os
import shlex
import subprocess
from shutil import which
from threading import Event
from typing import TYPE_CHECKING

from thingies.shell import MoreInformativeCalledProcessError

if TYPE_CHECKING:
    from .prompt_data import PromptData
    from .server import PromptEndingAction, ServerCall
from ..monitoring.Logger import get_logger
from .action_menu.binding import Binding, BindingConflict, ConflictResolution
from .action_menu.parametrized_actions import Action, ShellCommand
from .exceptions import ExitLoop
from .previewer import Preview, PreviewFunction, OnPreviewChange
from .prompt_data import PromptData, Result, ChoicesGetter, ReloadChoices
from .server import EndStatus, PostProcessor, PromptEndingAction, Server, ServerCall, ServerCallFunction

__all__ = [
    "run_fzf_prompt",
    "PromptData",
    "Result",
    "Binding",
    "BindingConflict",
    "Action",
    "ConflictResolution",
    "ShellCommand",
    "ChoicesGetter",
    "ReloadChoices",
    "ServerCall",
    "ServerCallFunction",
    "PromptEndingAction",
    "PostProcessor",
    "EndStatus",
    "Preview",
    "PreviewFunction",
    "OnPreviewChange",
]

# Black magic layer
# - Among other things, ensures communication between Python script and running fzf process
logger = get_logger()

FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable
def run_fzf_prompt[T, S](prompt_data: PromptData[T, S], *, executable_path=None) -> Result[T]:
    if not which("fzf") and not executable_path:
        raise SystemError(f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")
    else:
        executable_path = "fzf"

    if (automator := prompt_data.automator).should_run:
        automator.prepare()
        automator.start()

    prompt_data.previewer.resolve_main_preview()
    server_setup_finished = Event()
    server_should_close = Event()
    server = Server(prompt_data, server_setup_finished, server_should_close)
    server.start()
    server_setup_finished.wait()
    env = os.environ.copy()
    env["SOCKET_NUMBER"] = str(server.socket_number)

    # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
    try:
        options = prompt_data.resolve_options()
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
        server_should_close.set()
    server.join()
    if not prompt_data.finished:
        # TODO: This may be explicitly allowed in the future (need to test when it's not)
        raise RuntimeError("Prompt not finished (you aborted prompt without finishing PromptData)")
    if prompt_data.result.end_status == "quit":
        raise ExitLoop(f"Exiting app with\n{prompt_data.result}", prompt_data.result)
    prompt_data.apply_common_post_processors(prompt_data)
    return prompt_data.result
