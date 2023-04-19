import shlex
from typing import Callable, Generic, ParamSpec, Protocol

import clipboard

from .exceptions import ExitRound
from .intercom.PromptData import Preview, PromptData
from .MyFzfPrompt import Result
from .options import POSITION, Options
from .previews import PREVIEW
from .helpers.type_hints import Moddable


P = ParamSpec("P")


# TODO: compatibility with Typer? Or maybe modify Typer to accept it and ignore 'options'


# TODO: output preview
def add_options(added_options: Options):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def adding_options(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = prompt_data.options + added_options
            return func(prompt_data, *args, **kwargs)

        return adding_options

    return decorator


def exit_round_on_no_selection(message: str = ""):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def exiting_round_on_no_selection(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            if not (result := func(prompt_data, *args, **kwargs)) and not result.hotkey:
                raise ExitRound(message)
            return result

        return exiting_round_on_no_selection

    return decorator


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: command is can use Prompt attributes
# TODO: preview label
def preview(
    preview_: Preview,
    window_size: int | str = 75,
    window_position: str = POSITION.right,
):
    """formatter exists to parametrize the command based on self when wrapping a method"""

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            win_size = f"{window_size}%" if isinstance(window_size, int) else window_size
            print(preview_.command)
            preview_.command = preview_.command % prompt_data.id
            prompt_data.previews[preview_.id] = preview_
            prompt_data.options = Options(f"--preview-window {window_position},{win_size}") + prompt_data.options
            return func(
                prompt_data,
                *args,
                **kwargs,
            )

        return with_preview

    return decorator


# TODO: What if action needs attributes?
def hotkey(hk: str, action: str):
    """action shouldn't have single quotes in it"""

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_hotkey(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = Options().bind(hk, action) + prompt_data.options
            return func(prompt_data, *args, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hk: str, action: Callable):
    def deco(func: Moddable[P]) -> Moddable[P]:
        def with_python_hotkey(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = Options().expect(hk) + prompt_data.options
            result = func(prompt_data, *args, **kwargs)
            return action(result) if result.hotkey == hk else result

        return with_python_hotkey

    return deco


def clip_output(func: Moddable[P]) -> Moddable[P]:
    def clipping_output(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
        result = func(prompt_data, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
