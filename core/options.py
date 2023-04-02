from __future__ import annotations

import functools
from typing import Callable, ParamSpec, Self, Type, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

DEFAULT_OPTS = [
    "--layout=reverse",
    "--info=inline",
    "--cycle",
    "--no-mouse",
    "--bind=alt-shift-up:preview-half-page-up,alt-shift-down:preview-half-page-down",
    "--preview-window=wrap",
]


class OptionsAdder:
    """Does the same thing as a property. It exists to shorten code."""

    def __init__(self, *fzf_options: str):
        self._fzf_options = fzf_options

    def __get__(self, obj: Options, objtype: Type[Options] = None) -> Options:
        return obj.add(*self._fzf_options)


# TODO: tips formatter
class Options:
    defaults = OptionsAdder(*DEFAULT_OPTS)
    ansi = OptionsAdder("--ansi")
    no_sort = OptionsAdder("--no-sort")
    cycle = OptionsAdder("--cycle")
    no_mouse = OptionsAdder("--no-mouse")
    multiselect = OptionsAdder("--multi")
    header_first = OptionsAdder("--header-first")

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        """To use the object as a decorator"""

        @functools.wraps(func)
        def with_options(*args: P.args, **kwargs: P.kwargs):
            options = kwargs["options"]
            if not isinstance(options, Options):
                raise TypeError(f"options kw bad type: {type(options)}: {options}")
            kwargs["options"] = options + self
            return func(*args, **kwargs)

        return with_options

    def __init__(self, *fzf_options: str) -> None:
        self.__options: tuple[str, ...] = fzf_options

    @property
    def options(self) -> tuple[str, ...]:
        return self.__options

    def add(self, *fzf_options: str) -> Self:
        return self.__class__(*self.options, *fzf_options)

    def bind(self, hotkey: str, action: str):
        if isinstance(action, str):
            return self.add(f"--bind {hotkey}:{action}")

    def expect(self, *hotkeys: str):
        return self.add(f"--expect={','.join(hotkeys)}")

    def layout(self, layout: str):
        return self.add(f"--layout={layout}")

    def prompt(self, prompt: str):
        return self.add(f"--prompt='{prompt}'")

    def pointer(self, pointer: str):
        if len(pointer) > 2:
            raise ValueError(f"Pointer too long (should be max 2 chars): {pointer}")
        return self.add(f"--pointer='{pointer}'")

    def header(self, header: str):
        return self.add(f"--header='{header}'")

    def __str__(self) -> str:
        return " ".join(self.options)

    def __add__(self, __other: Options) -> Self:
        return self.add(*__other.options)

    # TODO: __sub__ for removing options?

    def __eq__(self, __other: Self) -> bool:
        return self.options == __other.options

    def __le__(self, __other: Self) -> bool:
        return self.options == __other.options[: len(self.options)]

    # Could've used functools.total_ordering here
    def __ge__(self, __other: Self) -> bool:
        return __other <= self

    def __lt__(self, __other: Self) -> bool:
        return self <= __other and len(self.options) < len(__other.options)

    def __gt__(self, __other: Self) -> bool:
        return __other < self


class LAYOUT:
    default = "default"
    reverse = "reverse"
    reverse_list = "reverse-list"


class BORDER:
    rounded = "rounded"
    sharp = "sharp"
    bold = "bold"
    double = "double"
    horizontal = "horizontal"
    vertical = "vertical"
    top = "top"
    bottom = "bottom"
    left = "left"
    right = "right"
    none = "none"


# TODO: fluent interface
class HOTKEY:
    ctrl_a = "ctrl-a"
    ctrl_b = "ctrl-b"
    ctrl_c = "ctrl-c"
    ctrl_d = "ctrl-d"
    ctrl_e = "ctrl-e"
    ctrl_f = "ctrl-f"
    ctrl_g = "ctrl-g"
    ctrl_h = "ctrl-h"
    ctrl_i = "ctrl-i"
    ctrl_j = "ctrl-j"
    ctrl_k = "ctrl-k"
    ctrl_l = "ctrl-l"
    ctrl_m = "ctrl-m"
    ctrl_n = "ctrl-n"
    ctrl_o = "ctrl-o"
    ctrl_p = "ctrl-p"
    ctrl_q = "ctrl-q"
    ctrl_r = "ctrl-r"
    ctrl_s = "ctrl-s"
    ctrl_t = "ctrl-t"
    ctrl_u = "ctrl-u"
    ctrl_v = "ctrl-v"
    ctrl_w = "ctrl-w"
    ctrl_x = "ctrl-x"
    ctrl_y = "ctrl-y"
    ctrl_z = "ctrl-z"
    ctrl_alt_a = "ctrl-alt-a"
    ctrl_alt_b = "ctrl-alt-b"
    ctrl_alt_c = "ctrl-alt-c"
    ctrl_alt_d = "ctrl-alt-d"
    ctrl_alt_e = "ctrl-alt-e"
    ctrl_alt_f = "ctrl-alt-f"
    ctrl_alt_g = "ctrl-alt-g"
    ctrl_alt_h = "ctrl-alt-h"
    ctrl_alt_i = "ctrl-alt-i"
    ctrl_alt_j = "ctrl-alt-j"
    ctrl_alt_k = "ctrl-alt-k"
    ctrl_alt_l = "ctrl-alt-l"
    ctrl_alt_m = "ctrl-alt-m"
    ctrl_alt_n = "ctrl-alt-n"
    ctrl_alt_o = "ctrl-alt-o"
    ctrl_alt_p = "ctrl-alt-p"
    ctrl_alt_q = "ctrl-alt-q"
    ctrl_alt_r = "ctrl-alt-r"
    ctrl_alt_s = "ctrl-alt-s"
    ctrl_alt_t = "ctrl-alt-t"
    ctrl_alt_u = "ctrl-alt-u"
    ctrl_alt_v = "ctrl-alt-v"
    ctrl_alt_w = "ctrl-alt-w"
    ctrl_alt_x = "ctrl-alt-x"
    ctrl_alt_y = "ctrl-alt-y"
    ctrl_alt_z = "ctrl-alt-z"
    enter = "enter"
    f1 = "f1"
    f2 = "f2"
    f3 = "f3"
    f4 = "f4"
    f5 = "f5"
    f6 = "f6"
    f7 = "f7"
    f8 = "f8"
    f9 = "f9"
    f10 = "f10"
    f11 = "f11"
    f12 = "f12"


class POSITION:
    up = "up"
    down = "down"
    left = "left"
    right = "right"


if __name__ == "__main__":
    pass
