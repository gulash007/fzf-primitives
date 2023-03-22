from __future__ import annotations
from typing import Self, Type

DEFAULT_OPTS = [
    "--layout=reverse",
    "--info=inline",
    "--cycle",
    "--no-mouse",
    "--bind=alt-shift-up:preview-half-page-up,alt-shift-down:preview-half-page-down",
    "--preview-window=wrap",
    "--expect=enter",
]


class OptionsAdder:
    """Does the same thing as a property. It exists to shorten code."""

    def __init__(self, *fzf_options: str):
        self._fzf_options = fzf_options

    def __get__(self, obj: Options, objtype: Type[Options] = None) -> Options:
        return obj.add(*self._fzf_options)


class Options:
    defaults = OptionsAdder(*DEFAULT_OPTS)
    ansi = OptionsAdder("--ansi")
    no_sort = OptionsAdder("--no-sort")
    cycle = OptionsAdder("--cycle")
    no_mouse = OptionsAdder("--no-mouse")
    multiselect = OptionsAdder("--multi")

    def __call__(self, func):
        """To use the object as a decorator"""

        def with_options(slf, options: Options = Options(), *args, **kwargs):
            return func(slf, options + self, *args, **kwargs)

        return with_options

    def __init__(self, *options: str) -> None:
        self.options: tuple[str, ...] = options

    def add(self, *additional_options: str) -> Self:
        return type(self)(*self.options, *additional_options)

    def bind(self, hotkey: str, action: Callable | str):
        if isinstance(action, str):
            return self.add(f"--bind {hotkey}:{action}")

    def expect(self, *hotkeys: str):
        return self.add(f"--expect={','.join(hotkeys)}")

    def layout(self, layout: str):
        return self.add(f"--layout={layout}")

    def __str__(self) -> str:
        return " ".join(self.options)

    def __add__(self, __other: Options) -> Self:
        return self.add(*__other.options)

    # TODO: __sub__ for removing options?

    def __eq__(self, __other: Self) -> bool:
        return self.options == __other.options

    def __le__(self, __other: Self) -> bool:
        return self.options == __other.options[: len(self.options)]

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


if __name__ == "__main__":
    pass
