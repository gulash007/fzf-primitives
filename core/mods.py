# Syntax sugar layer

import functools
import shlex
from typing import Callable, Generic, ParamSpec, Protocol
from enum import Enum

import clipboard

from .exceptions import ExitRound
from .FzfPrompt.options import Hotkey, Options, Position
from .FzfPrompt.Previewer import Preview
from .FzfPrompt.previews import PREVIEW
from .FzfPrompt.Prompt import Result
from .FzfPrompt.PromptData import PromptData
from .FzfPrompt.descriptors import preset

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


multiselect = add_options(Options().multiselect)
ansi = add_options(Options().ansi)
no_sort = add_options(Options().no_sort)


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


class preview:
    basic = preset(Preview)("basic")
    custom = Preview


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
