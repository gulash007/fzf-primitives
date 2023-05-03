# Syntax sugar layer

import functools
from typing import Any, Callable, Generic, ParamSpec, Protocol

import clipboard

from .exceptions import ExitRound
from .FzfPrompt.ActionMenu import Action
from .FzfPrompt.decorators import constructor
from .FzfPrompt.options import Hotkey, Options
from .FzfPrompt.Previewer import Preview
from .FzfPrompt.Prompt import Result
from .FzfPrompt.PromptData import PromptData
from .monitoring.Logger import get_logger

P = ParamSpec("P")
logger = get_logger()


class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...


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
                logger.info(message)
                raise ExitRound(message)
            return result

        return exiting_round_on_no_selection

    return decorator


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: command is can use Prompt attributes
# TODO: preview label


get_preview = constructor(Preview)


class preview:
    basic = functools.partial(get_preview, "basic", None)
    custom = staticmethod(get_preview)  # without staticmethod decorator get_preview is treated like instance method


# TODO: What if action needs attributes?
def hotkey(hk: Hotkey, action: str):
    """action shouldn't have single quotes in it"""

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_hotkey(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = Options().bind(hk, action) + prompt_data.options
            return func(prompt_data, *args, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hk: Hotkey, result_processor: Callable[[Result], Any]):
    def deco(func: Moddable[P]) -> Moddable[P]:
        def with_python_hotkey(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options.expect(hk)
            prompt_data.action_menu.add(Action(result_processor.__name__, "accept", hk))
            result = func(prompt_data, *args, **kwargs)
            return result_processor(result) if result.hotkey == hk else result

        return with_python_hotkey

    return deco


def clip_output(func: Moddable[P]) -> Moddable[P]:
    def clipping_output(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
        result = func(prompt_data, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
