from __future__ import annotations

import shlex
from typing import Self

from .actions import BaseAction, ParametrizedActionType, ShellCommandActionType
from .events import Hotkey, Situation
from .values import Border, EndStatus, Layout, RelativeWindowSize, WindowPosition

DEFAULT_OPTS = [
    "--layout=reverse",
    "--info=inline",
    "--cycle",
    "--no-mouse",
    "--bind=alt-shift-up:preview-half-page-up,alt-shift-down:preview-half-page-down",
    "--preview-window=wrap",
]

# TODO: Add more options (see unused imports)


class OptionsAdder:
    """Does the same thing as a property. It exists to shorten code.
    It also signals that it might do something unexpected of a property."""

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
    disable_search = OptionsAdder("--disabled")
    sync = OptionsAdder("--sync")

    # TODO: Make it a dict

    def __init__(self, *fzf_options: str) -> None:
        self.__options: list[str] = list(fzf_options)
        self._header_strings: list[str] = []

    @property
    def options(self) -> list[str]:
        return self.__options

    def add(self, *fzf_options: str) -> Self:
        self.options.extend(fzf_options)
        return self

    def initial_query(self, query: str) -> Self:
        return self.add(f"--query={query}")

    def multiselect_with_limit(self, limit: int) -> Self:
        return self.add(f"--multi={limit}")

    def preview(self, command: str) -> Self:
        return self.add(f"--preview={command}")

    def preview_window(
        self, position: WindowPosition, size: int | RelativeWindowSize, *, line_wrap: bool = True
    ) -> Self:
        return self.add(f"--preview-window={position},{size}:{'wrap' if line_wrap else 'nowrap'}")

    def preview_label(self, label: str) -> Self:
        return self.add(f"--preview-label={label}")

    def bind(self, event: Hotkey | Situation, action: str) -> Self:
        return self.add(f"--bind={event}:{action}")

    def bind_base_action(self, event: Hotkey | Situation, action: BaseAction) -> Self:
        return self.bind(event, action)

    def bind_shell_command(
        self, event: Hotkey | Situation, command: str, command_type: ShellCommandActionType = "execute"
    ) -> Self:
        return self.bind(event, f"{command_type}({command})")

    def expect(self, *hotkeys: Hotkey) -> Self:
        return self.add(f"--expect={','.join(hotkeys)}")

    def border(self, border: Border, label: str) -> Self:
        return self.add(f"--border={border}", f"--border-label={label}")

    def layout(self, layout: Layout) -> Self:
        return self.add(f"--layout={layout}")

    def prompt(self, prompt: str) -> Self:
        return self.add(f"--prompt={prompt}")

    def pointer(self, pointer: str) -> Self:
        if len(pointer) > 2:
            raise ValueError(f"Pointer too long (should be max 2 chars): {pointer}")
        return self.add(f"--pointer={pointer}")

    def with_nth_column(self, field_index_expression: str, delimiter: str | None = None) -> Self:
        """Transform the presentation of each line using field index expressions

        Delimiter is AWK style by default
        """
        args = [f"--with-nth={field_index_expression}"]
        if delimiter:
            args.append(f"--delimiter={delimiter}")
        return self.add(*args)

    def add_header(self, header: str) -> Self:
        self._header_strings.append(header)
        return self

    @property
    def header_option(self) -> str:
        return f"--header={'\n'.join(self._header_strings)}"

    def listen(self, port_number: int = 0):
        return self.add(f"--listen={port_number}")

    def __str__(self) -> str:
        return shlex.join(self)

    def __iter__(self):
        options = self.options.copy()
        if self._header_strings:
            options.append(self.header_option)
        return iter(options)

    def pretty(self) -> str:
        return "\n".join([shlex.quote(option) for option in self])

    def __add__(self, __other: Options) -> Self:
        options = self.add(*__other.options)
        options._header_strings += __other._header_strings
        return options

    # TODO: __sub__ for removing options?

    def __eq__(self, __other: Self) -> bool:
        return self.options == __other.options and self._header_strings == __other._header_strings
