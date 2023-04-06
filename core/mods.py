from typing import Callable

import clipboard

from .exceptions import ExitRound
from .helpers.type_hints import ModdableMethod, P, R
from .MyFzfPrompt import Result
from .options import HOTKEY, POSITION, Options
from .Prompt import Prompt

# ❗ options have to be passed keyworded


def add_options(added_options: Options):
    def decorator(func: ModdableMethod[P, R]) -> ModdableMethod[P, R]:
        def adding_options(self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            return func(self, options=options + added_options, *args, **kwargs)

        return adding_options

    return decorator


def exit_round_on_no_selection(message: str = ""):
    def decorator(func: ModdableMethod[P, Result]) -> ModdableMethod[P, Result]:
        def exiting_round_on_no_selection(
            self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs
        ):
            if not (result := func(self, options, *args, **kwargs)) and not result.hotkey:
                raise ExitRound(message)
            return result

        return exiting_round_on_no_selection

    return decorator


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: command is can use Prompt attributes
def preview(
    command: str,
    window_size: int | str = 75,
    window_position: str = POSITION.right,
    live_clip_preview: bool = False,
):
    """formatter exists to parametrize the command based on self when wrapping a method"""
    command = f"{command} | tee >(clip)" if live_clip_preview else command

    def decorator(func: ModdableMethod[P, R]) -> ModdableMethod[P, R]:
        def with_preview(self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            # print(type(self))
            win_size = f"{window_size}%" if isinstance(window_size, int) else window_size
            return func(
                self,
                options=Options(
                    f"{options} --preview-window={window_position},{win_size} --preview 'echo && {command}'"
                )
                + options,
                *args,
                **kwargs,
            )

        return with_preview

    return decorator


# TODO: What if action needs attributes?
def hotkey(hk: str, action: Callable | str):
    """action shouldn't have single quotes in it"""

    def decorator(func: ModdableMethod[P, R]) -> ModdableMethod[P, R]:
        def with_hotkey(self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            return func(self, options=Options(f"--bind={hk}:'{action}'") + options, *args, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hk: str, action: Callable):
    def deco(func: ModdableMethod[P, Result]) -> ModdableMethod[P, Result]:
        def with_python_hotkey(self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            result = func(self, options=Options().expect(hk) + options, *args, **kwargs)
            return action(result) if result.hotkey == hk else result

        return with_python_hotkey

    return deco


def clip_output(func: ModdableMethod[P, Result]) -> ModdableMethod[P, Result]:
    def clipping_output(self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
        result = func(self, options=options, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
