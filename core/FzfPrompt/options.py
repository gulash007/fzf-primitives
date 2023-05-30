# Black magic layer
from __future__ import annotations

import shlex
from typing import Literal, Self


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

    def __get__(self, obj: Options, objtype: type[Options] | None = None) -> Options:
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

    # TODO: Make it a dict

    @classmethod
    def __get_validators__(cls):
        return ()

    def __init__(self, *fzf_options: str) -> None:
        self.__options: list[str] = list(fzf_options)

    @property
    def options(self) -> list[str]:
        return self.__options

    def add(self, *fzf_options: str) -> Self:
        self.options.extend(fzf_options)
        return self

    def preview(self, command: str) -> Self:
        return self.add(shlex.join(["--preview", f"{command}"]))

    def preview_label(self, label: str) -> Self:
        return self.add(shlex.join(["--preview-label", label]))

    def bind(self, event: Hotkey | Event, action: str) -> Self:
        return self.add(shlex.join(["--bind", f"{event}:{action}"]))

    def on_event(self, event: Event, action: str) -> Self:
        return self.add(shlex.join(["--bind", f"{event}:{action}"]))

    def expect(self, *hotkeys: Hotkey) -> Self:
        return self.add(shlex.join(["--expect", f"{','.join(hotkeys)}"]))

    def layout(self, layout: str) -> Self:
        return self.add(shlex.join(["--layout", layout]))

    def prompt(self, prompt: str) -> Self:
        return self.add(shlex.join(["--prompt", prompt]))

    def pointer(self, pointer: str) -> Self:
        if len(pointer) > 2:
            raise ValueError(f"Pointer too long (should be max 2 chars): {pointer}")
        return self.add(shlex.join(["--pointer", pointer]))

    def header(self, header: str) -> Self:
        return self.add(shlex.join(["--header", header]))

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


Layout = Literal[
    "default",
    "reverse",
    "reverse-list",
]
Border = Literal[
    "rounded",
    "sharp",
    "bold",
    "double",
    "horizontal",
    "vertical",
    "top",
    "bottom",
    "left",
    "right",
    "none",
]
Position = Literal[
    "up",
    "down",
    "left",
    "right",
]
Event = Literal["change", "focus"]
Hotkey = Literal[
    "ctrl-a",
    "ctrl-b",
    "ctrl-c",
    "ctrl-d",
    "ctrl-e",
    "ctrl-f",
    "ctrl-g",
    "ctrl-h",
    "ctrl-i",
    "ctrl-j",
    "ctrl-k",
    "ctrl-l",
    "ctrl-m",
    "ctrl-n",
    "ctrl-o",
    "ctrl-p",
    "ctrl-q",
    "ctrl-r",
    "ctrl-s",
    "ctrl-t",
    "ctrl-u",
    "ctrl-v",
    "ctrl-w",
    "ctrl-x",
    "ctrl-y",
    "ctrl-z",
    "ctrl-6",
    "alt-a",
    "alt-b",
    "alt-c",
    "alt-d",
    "alt-e",
    "alt-f",
    "alt-g",
    "alt-h",
    "alt-i",
    "alt-j",
    "alt-k",
    "alt-l",
    "alt-m",
    "alt-n",
    "alt-o",
    "alt-p",
    "alt-q",
    "alt-r",
    "alt-s",
    "alt-t",
    "alt-u",
    "alt-v",
    "alt-w",
    "alt-x",
    "alt-y",
    "alt-z",
    "alt-0",
    "alt-1",
    "alt-2",
    "alt-3",
    "alt-4",
    "alt-5",
    "alt-6",
    "alt-7",
    "alt-8",
    "alt-9",
    "alt-0",
    "alt-up",
    "alt-down",
    "ctrl-alt-a",
    "ctrl-alt-b",
    "ctrl-alt-c",
    "ctrl-alt-d",
    "ctrl-alt-e",
    "ctrl-alt-f",
    "ctrl-alt-g",
    "ctrl-alt-h",
    "ctrl-alt-i",
    "ctrl-alt-j",
    "ctrl-alt-k",
    "ctrl-alt-l",
    "ctrl-alt-m",
    "ctrl-alt-n",
    "ctrl-alt-o",
    "ctrl-alt-p",
    "ctrl-alt-q",
    "ctrl-alt-r",
    "ctrl-alt-s",
    "ctrl-alt-t",
    "ctrl-alt-u",
    "ctrl-alt-v",
    "ctrl-alt-w",
    "ctrl-alt-x",
    "ctrl-alt-y",
    "ctrl-alt-z",
    "enter",
    "esc",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
]


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
    ctrl_6 = "ctrl-6"  # the only number that's working
    alt_a = "alt-a"
    alt_b = "alt-b"
    alt_c = "alt-c"
    alt_d = "alt-d"
    alt_e = "alt-e"
    alt_f = "alt-f"
    alt_g = "alt-g"
    alt_h = "alt-h"
    alt_i = "alt-i"
    alt_j = "alt-j"
    alt_k = "alt-k"
    alt_l = "alt-l"
    alt_m = "alt-m"
    alt_n = "alt-n"
    alt_o = "alt-o"
    alt_p = "alt-p"
    alt_q = "alt-q"
    alt_r = "alt-r"
    alt_s = "alt-s"
    alt_t = "alt-t"
    alt_u = "alt-u"
    alt_v = "alt-v"
    alt_w = "alt-w"
    alt_x = "alt-x"
    alt_y = "alt-y"
    alt_z = "alt-z"
    alt_0 = "alt-0"
    alt_1 = "alt-1"
    alt_2 = "alt-2"
    alt_3 = "alt-3"
    alt_4 = "alt-4"
    alt_5 = "alt-5"
    alt_6 = "alt-6"
    alt_7 = "alt-7"
    alt_8 = "alt-8"
    alt_9 = "alt-9"
    alt_0 = "alt-0"
    alt_up = "alt-up"
    alt_down = "alt-down"
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
    enter = "enter"  # usually reserved for accepting a selection
    esc = "esc"  # usually reserved for exiting with no selection
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


if __name__ == "__main__":
    print(Options("fzf").bind("ctrl-q", "execute(echo && echo hello)"))
