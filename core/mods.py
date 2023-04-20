# Syntax sugar layer

import shlex
from typing import Callable, Generic, ParamSpec, Protocol

import clipboard

from .exceptions import ExitRound
from .FzfPrompt.PromptData import PreviewName, PromptData
from .FzfPrompt.Prompt import Result
from .FzfPrompt.options import Position, Hotkey, Options
from .FzfPrompt.previews import PREVIEW


P = ParamSpec("P")


# TODO: compatibility with Typer? Or maybe modify Typer to accept it and ignore 'options'
class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...


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
def preview(preview_name: PreviewName, window_size: int | str = "50%", window_position: Position = "right"):
    """formatter exists to parametrize the command based on self when wrapping a method"""

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_preview(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.add_preview(preview_name, window_size, window_position)
            return func(
                prompt_data,
                *args,
                **kwargs,
            )

        return with_preview

    return decorator


# TODO: What if action needs attributes?
def hotkey(hk: Hotkey, action: str):
    """action shouldn't have single quotes in it"""

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_hotkey(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = Options().bind(hk, action) + prompt_data.options
            return func(prompt_data, *args, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hk: Hotkey, action: Callable):
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
