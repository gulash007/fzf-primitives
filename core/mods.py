from typing import Callable

import clipboard

from .exceptions import ExitRound
from .helpers.type_hints import Moddable, P
from .options import Options, POSITION


# TODO: output preview
def add_options(added_options: Options):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def adding_options(options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            return func(options=options + added_options, *args, **kwargs)

        return adding_options

    return decorator


def exit_round_on_no_selection(message: str = ""):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def exiting_round_on_no_selection(options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            if not (result := func(options, *args, **kwargs)) and not result.hotkey:
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

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_preview(options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            # print(type(self))
            win_size = f"{window_size}%" if isinstance(window_size, int) else window_size
            return func(
                options=Options(f"--preview-window={window_position},{win_size} --preview 'echo && {command}'")
                + options,
                *args,
                **kwargs,
            )

        return with_preview

    return decorator


# TODO: What if action needs attributes?
def hotkey(hk: str, action: str):
    """action shouldn't have single quotes in it"""

    def decorator(func: Moddable[P]) -> Moddable[P]:
        def with_hotkey(options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            return func(options=Options().bind(hk, action) + options, *args, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hk: str, action: Callable):
    def deco(func: Moddable[P]) -> Moddable[P]:
        def with_python_hotkey(options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
            result = func(options=Options().expect(hk) + options, *args, **kwargs)
            return action(result) if result.hotkey == hk else result

        return with_python_hotkey

    return deco


def clip_output(func: Moddable[P]) -> Moddable[P]:
    def clipping_output(options: Options = Options(), *args: P.args, **kwargs: P.kwargs):
        result = func(options=options, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
