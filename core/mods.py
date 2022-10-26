from typing import Any, Callable, TypeVar

import clipboard
from thingies import decorator

from core.exceptions import ExitLoop, ExitRound

T = TypeVar("T")


def add_option(option: str):
    @decorator
    def with_added_option(func, self, options: str, *args, **kwargs):
        return func(self, f"{options} {option}", *args, **kwargs)

    return with_added_option


DEFAULT_OPTS = "--layout=reverse --info=inline --cycle --no-mouse --bind alt-shift-up:preview-half-page-up,alt-shift-down:preview-half-page-down --preview-window=wrap"
defaults = add_option(DEFAULT_OPTS)
ansi = add_option("--ansi")
multiselect = add_option("--multi")
no_sort = add_option("--no-sort")  # AKA +p


@decorator
def exit_on_no_selection(func, self, options, *args, **kwargs):
    if output := func(self, options, *args, **kwargs):
        return output
    raise ExitRound  # TODO: custom message (decorator factory)


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: command is can use Prompt attributes
def preview(
    window_size: int,
    command: str,
    formatter: Callable[[Any, str], str] = lambda self, command: command,
    live_clip_preview: bool = False,
):
    command = f"{command} | tee >(clip)" if live_clip_preview else command

    @decorator
    def wrapped(func, self, options: str, *args, **kwargs):
        cmd = formatter(self, command)
        # ❓ for some reason, 'command' can't be reassigned with its transformation as it leads to 'command' being unbound
        return func(self, f"{options} --preview-window=right,{window_size}% --preview 'echo && {cmd}'", *args, **kwargs)

    return wrapped


# TODO: needs decorator factory decorator
# TODO: consumes the hotkey, but what if I need the hotkey?
@decorator
def exit_hotkey(func, self, options, *args, **kwargs):
    """Should produce a signal (raise an Exception) to end loop"""
    output = func(self, f"{options} --expect=ctrl-q", *args, **kwargs)
    if output and output[0] == "ctrl-q":
        raise ExitLoop
    return output[1:]


def hotkey(f: Callable):
    pass


@decorator
def clip_output(func, self, options, *args, **kwargs):
    output = func(self, options, *args, **kwargs)
    clipboard.copy("\n".join(output) if isinstance(output, list) else output)
    return output
