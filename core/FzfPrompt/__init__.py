from __future__ import annotations

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
from .controller import Controller
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
    EndStatus,
    PostProcessor,
    PromptEndingAction,
    ServerCall,
    ServerCallFunction,
    ServerEndpoint,
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
    "Controller",
]


FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable
# Inspired by https://github.com/nk412/pyfzf
def run_fzf_prompt[T, S](prompt_data: PromptData[T, S], *, executable_path=None) -> Result[T]:
    try:
        logger = Logger.get_logger()

        prompt_data.run_initial_setup()
        server = prompt_data.server
        server.start()
        server.setup_finished.wait()
        executable_path = executable_path or "fzf"
        prompt_data.run_vars["executable_path"] = executable_path

        # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
        try:
            options = prompt_data.options
            logger.debug(f"Running fzf with options:\n{options.pretty()}")
            subprocess.run(
                [executable_path, *options],
                shell=False,
                input=prompt_data.choices_string.encode(),
                check=True,
                env=prompt_data.run_vars["env"],
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
        if prompt_data.stage != "finished":
            # TODO: This may be explicitly allowed in the future (need to test when it's not)
            raise RuntimeError("Prompt not finished (you aborted prompt without finishing PromptData)")
        if prompt_data.result.end_status == "quit":
            raise Quitting(f"Exiting app with\n{prompt_data.result}", prompt_data.result)
        event = prompt_data.result.event
        if not (final_action := prompt_data.action_menu.bindings[event].final_action):
            raise RuntimeError("Prompt ended on event that doesn't have final action. How did we get here?")
        if final_action.post_processor:
            final_action.post_processor(prompt_data)
    finally:
        for post_processor in prompt_data.post_processors:
            post_processor(prompt_data)
    return prompt_data.result


class FzfExecutionError(Exception):
    pass
