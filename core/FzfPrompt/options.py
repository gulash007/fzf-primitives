# Black magic layer
from __future__ import annotations

import shlex
from string import Template
from typing import Iterable, Literal, Self, Any, Type, TypeVar, ParamSpec, get_args


P = ParamSpec("P")

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
    disable_search = OptionsAdder("--disabled")

    # TODO: Make it a dict

    @classmethod
    def __get_validators__(cls):
        return ()

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
        return self.add(shlex.join(["--query", query]))

    def preview(self, command: str) -> Self:
        return self.add(shlex.join(["--preview", f"{command}"]))

    def preview_window(self, position: Position, size: int | str) -> Self:
        return self.add(shlex.join(["--preview-window", f"{position},{size}"]))

    def preview_label(self, label: str) -> Self:
        return self.add(shlex.join(["--preview-label", label]))

    def bind(self, event: Hotkey | FzfEvent, action: str) -> Self:
        return self.add(shlex.join(["--bind", f"{event}:{action}"]))

    def bind_base_action(self, event: Hotkey | FzfEvent, action: BaseAction) -> Self:
        return self.bind(event, action)

    def bind_shell_command(
        self, event: Hotkey | FzfEvent, command: str, command_type: ShellCommandActionType = "execute"
    ) -> Self:
        return self.bind(event, f"{command_type}({command})")

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
        self._header_strings.append(header)
        return self

    @property
    def header_option(self) -> str:
        return shlex.join(["--header", "\n".join(self._header_strings)])

    def listen(self, port_number: int = 0):
        return self.add(f"--listen={port_number}")

    def __str__(self) -> str:
        options = self.options.copy()
        if self._header_strings:
            options.append(self.header_option)
        return " ".join(options)

    def pretty(self) -> str:
        options = self.options.copy()
        if self._header_strings:
            options.append(self.header_option)
        return "\n".join(options)

    def __add__(self, __other: Options) -> Self:
        options = self.add(*__other.options)
        options._header_strings += __other._header_strings
        return options

    # TODO: __sub__ for removing options?

    def __eq__(self, __other: Self) -> bool:
        return self.options == __other.options and self._header_strings == __other._header_strings


T = TypeVar("T")


class RemembersHowItWasConstructed(type):
    def __call__(cls: Type[T], *args, **kwargs) -> T:
        instance = super().__call__(*args, **kwargs)
        setattr(instance, "_new_copy", lambda: cls(*args, **kwargs))
        return instance


class ParametrizedOptionString(metaclass=RemembersHowItWasConstructed):
    def __init__(self, template: str, placeholders_to_resolve: Iterable[str] = ()) -> None:
        """
        Args:
            template (str): Should contain placeholders in the format: $some_placeholder (same as bash variable)
            placeholders_to_resolve (Iterable[str], optional): An iterable of placeholders that are required
            to be resolved before this object is used in a fzf option.
            Defaults to ().
        """
        self.template = template
        self.placeholders_to_resolve = set(placeholders_to_resolve)
        self.resolved_placeholders: dict[str, Any] = {}

    @property
    def resolved(self) -> bool:
        return set(self.resolved_placeholders) == self.placeholders_to_resolve

    def resolve(self, **mapping):
        for key, value in mapping.items():
            if key not in self.placeholders_to_resolve:
                raise RuntimeError(f"{self}: {key} not in {self.placeholders_to_resolve=}")
            if key in self.resolved_placeholders:
                raise RuntimeError(f"{self}: {key} already resolved")
            self.resolved_placeholders.update({key: value})

    def to_action_string(self) -> str:
        """To resolve into action string that can be used in --bind '<event>:<action string>'"""
        if not self.resolved:
            raise NotResolved(f"{self}: {self.placeholders_to_resolve.difference(self.resolved_placeholders)}")
        return Template(self.template).safe_substitute(self.resolved_placeholders)

    def __str__(self) -> str:
        return f"{super().__str__()} with template '{self.template}'"

    def new_copy(self) -> Self:
        """Returns a fresh (unresolved) copy as if you were to construct this object anew with original arguments.
        ❗ Doesn't create copies of the arguments themselves."""
        return getattr(self, "_new_copy")()


class NotResolved(RuntimeError): ...


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
FzfEvent = Literal[
    "start",
    "load",
    "change",
    "focus",
    "one",
    "backward-eof",
]
# raw fzf actions that aren't parametrized
BaseAction = Literal[
    "accept",
    "abort",
    "up",
    "down",
    "clear-query",
    "select",
    "select-all",
    "toggle",
    "toggle-all",
    "refresh-preview",
    "toggle-preview",
    "jump",
    "jump-accept",
]
ShellCommandActionType = Literal[
    "execute",
    "execute-silent",
    "change-preview",
]
# TODO: Add more available keys
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


def get_hotkey_set() -> set[Hotkey]:
    hotkeys = list(get_args(Hotkey))
    return set(hotkeys)


if __name__ == "__main__":
    print(Options("fzf").bind("ctrl-q", "execute(echo && echo hello)"))
