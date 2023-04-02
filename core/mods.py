import functools
from typing import Callable

import clipboard

from .exceptions import ExitRound
from .MyFzfPrompt import Result
from .options import POSITION, Options

# ❗ options have to be passed keyworded


def add_options(added_options: Options):
    def decorator(func):
        @functools.wraps(func)
        def adding_options(*args, options: Options = Options(), **kwargs):
            return func(*args, options=options + added_options, **kwargs)

        return adding_options

    return decorator


def exit_round_on_no_selection(func):
    def exiting_round_on_no_selection(*args, options: Options = Options(), **kwargs):
        if not (result := func(*args, options=options, **kwargs)):
            raise ExitRound  # TODO: custom message (decorator factory)
        return result

    return exiting_round_on_no_selection


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

    def decorator(func):
        @functools.wraps(func)
        def with_preview(*args, options: Options = Options(), **kwargs):
            # print(type(self))
            win_size = f"{window_size}%" if isinstance(window_size, int) else window_size
            return func(
                *args,
                options=Options(
                    f"{options} --preview-window={window_position},{win_size} --preview 'echo && {command}'"
                )
                + options,
                **kwargs,
            )

        return with_preview

    return decorator


# TODO: What if action needs attributes?
def hotkey(hk: str, action: Callable | str):
    """action shouldn't have single quotes in it"""

    def decorator(func):
        @functools.wraps(func)
        def with_hotkey(*args, options: Options = Options(), **kwargs):
            # print(options, *args, **kwargs)
            # print(hotkey, action)
            return func(*args, options=Options(f"--bind={hk}:'{action}'") + options, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hk: str, action: Callable):
    def deco(func):
        def with_python_hotkey(*args, options: Options = Options(), **kwargs):
            result: Result = func(*args, options=Options().expect(hk) + options, **kwargs)
            return action(result) if result.hotkey == hk else result

        return with_python_hotkey

    return deco


def clip_output(func):
    @functools.wraps(func)
    def clipping_output(*args, options: Options = Options(), **kwargs):
        result: Result = func(*args, options=options, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
