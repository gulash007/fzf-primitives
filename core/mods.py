import functools
from typing import Any, Callable, Optional

import clipboard
from core.MyFzfPrompt import Result

from core.exceptions import ExitLoop, ExitRound
from core.options import Options, HOTKEY, POSITION

# FUNCTION DECORATOR


def add_options(added_options: Options):
    def decorator(func):
        @functools.wraps(func)
        def adding_options(self, options: Options = Options(), *args, **kwargs):
            return func(self, options + added_options, *args, **kwargs)

        return adding_options

    return decorator


def exit_round_on_no_selection(func):
    def exiting_round_on_no_selection(self, options: Options = Options(), *args, **kwargs):
        if not (result := func(self, options, *args, **kwargs)):
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
    formatter: Optional[Callable[[Any, str], str]] = None,
    live_clip_preview: bool = False,
):
    """formatter exists to parametrize the command based on self when wrapping a method"""
    command = f"{command} | tee >(clip)" if live_clip_preview else command

    def decorator(func):
        @functools.wraps(func)
        def with_preview(self, options: Options = Options(), *args, **kwargs):
            # print(type(self))
            cmd = formatter(self, command) if formatter else command
            win_size = f"{window_size}%" if isinstance(window_size, int) else window_size
            # ❓ for some reason, 'command' can't be reassigned with its transformation as it leads to 'command' being unbound
            # ❗ since 'cmd' is unwrapped between single quotes, if it contains single quoted stuff, it might break the whole thing (calling out some unexpected token shit)
            return func(
                self,
                Options(f"{options} --preview-window={window_position},{win_size} --preview 'echo && {cmd}'") + options,
                *args,
                **kwargs,
            )

        return with_preview

    return decorator


# TODO: needs decorator factory decorator
# TODO: consumes the hotkey, but what if I need the hotkey?
def exit_loop_hotkey(func):
    def with_exit_loop_hotkey(self, options: Options = Options(), *args, **kwargs):
        """Should produce a signal (raise an Exception) to end loop"""
        result: Result = func(self, Options(f"--expect={HOTKEY.ctrl_q}") + options, *args, **kwargs)
        if result.hotkey == HOTKEY.ctrl_q:
            raise ExitLoop
        return result

    return with_exit_loop_hotkey


# def hotkey(hotkey: str, action: str):
#     @decorator
#     def wrapped(func, self, options: Options, *args, **kwargs):
#         return func(self, f"{options} --bind={hotkey}:{action}", *args, **kwargs)

#     return wrapped


# TODO: What if action needs attributes?
def hotkey(hotkey: str, action: Callable | str):
    """action shouldn't have single quotes in it"""

    def decorator(func):
        @functools.wraps(func)
        def with_hotkey(self, options: Options = Options(), *args, **kwargs):
            # print(options, *args, **kwargs)
            # print(hotkey, action)
            return func(self, Options(f"--bind={hotkey}:'{action}'") + options, *args, **kwargs)

        return with_hotkey

    return decorator


def hotkey_python(hotkey: str, action: Callable):
    def deco(func):
        def wrapper(self, options: Options = Options(), *args, **kwargs):
            result: Result = func(self, Options().expect(hotkey) + options, *args, **kwargs)
            return action(self, result) if result.consume(hotkey) else result

        return wrapper

    return deco


def clip_output(func):
    @functools.wraps(func)
    def clipping_output(self, options: Options = Options(), *args, **kwargs):
        result: Result = func(self, options, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output


# class SomeCl:
#     # def choose_file(self, )

#     @quit_hotkey
#     @hotkey("h1", "a1")
#     def choose_line(self, options: Options = Options(), filename: str = ""):
#         pass


# s = SomeCl()
# s.choose_line("help", "me")
