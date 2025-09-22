from __future__ import annotations

import shlex
from typing import Self

from .actions import BaseAction, ParametrizedActionType, ShellCommandActionType
from .triggers import Event, Hotkey
from .values import (
    Algorithm,
    Border,
    Info,
    LabelPosition,
    Layout,
    RelativeWindowSize,
    Scheme,
    Tiebreak,
    WalkerValue,
    WindowPosition,
)

# TODO: move to some config
DEFAULT_OPTS = [
    "--layout=reverse",
    "--info=inline",
    "--cycle",
    "--no-mouse",
    "--bind=alt-shift-up:preview-half-page-up,alt-shift-down:preview-half-page-down",
    "--preview-window=wrap",
]


class OptionsAdder:
    """Does the same thing as a property. It exists to shorten code.
    It also signals that it might do something unexpected of a property."""

    def __init__(self, *fzf_options: str):
        self._fzf_options = fzf_options

    def __get__(self, obj: Options, objtype: type[Options] | None = None) -> Options:
        return obj.add(*self._fzf_options)


# TODO: tips formatter
# TODO: add options lookup
class Options:
    defaults = OptionsAdder(*DEFAULT_OPTS)

    # TODO: Make it a dict

    def __init__(self, *fzf_options: str) -> None:
        self.__options: list[str] = list(fzf_options)
        self._header_strings: list[str] = []
        self._footer_strings: list[str] = []

    @property
    def options(self) -> list[str]:
        return self.__options

    def add(self, *fzf_options: str) -> Self:
        self.options.extend(fzf_options)
        return self

    # SEARCH
    extended = OptionsAdder("--extended")
    no_extended = OptionsAdder("--no-extended")
    exact = OptionsAdder("--exact")
    no_exact = OptionsAdder("--no-exact")
    ignore_case = OptionsAdder("--ignore-case")
    no_ignore_case = OptionsAdder("--no-ignore-case")
    smart_case = OptionsAdder("--smart-case")
    literal = OptionsAdder("--literal")
    no_literal = OptionsAdder("--no-literal")

    def scheme(self, scheme: Scheme) -> Self:
        """Choose scoring scheme tailored for different types of input.

        values:
            - default: Generic scoring scheme designed to work well with any type of input.
            - path: Additional bonus point is only given to the characters after path separator.  You might want to choose this scheme over
                default if you have many files with spaces in their paths. This also sets --tiebreak=pathname,length, to prioritize
                matches occurring in the tail element of a file path.
            - history: Scoring scheme well suited for command history or any input where chronological ordering is important. No additional
                bonus points are given so that we give more weight to the chronological ordering. This also sets --tiebreak=index.
        """
        return self.add(f"--scheme={scheme}")

    def algo(self, algo: Algorithm) -> Self:
        """Fuzzy matching algorithm (default: v2)

        values:
            - v1: Optimal scoring algorithm (quality)
            - v2: Faster but not guaranteed to find the optimal result (performance)
        """
        return self.add(f"--algo={algo}")

    def nth(self, field_index_expression: str) -> Self:
        """Comma-separated list of field index expressions for limiting search scope."""
        return self.add(f"--nth={field_index_expression}")

    def with_nth_column(self, field_index_expression: str) -> Self:
        """Transform the presentation of each line using field index expressions

        Delimiter is AWK style by default
        """
        return self.add(f"--with-nth={field_index_expression}")

    def accept_nth(self, field_index_expression: str) -> Self:
        return self.add(f"--accept-nth={field_index_expression}")

    no_sort = OptionsAdder("--no-sort")

    def delimiter(self, delimiter: str | None = None) -> Self:
        return self.add(f"--delimiter={delimiter}")

    def tail(self, n: int) -> Self:
        """Maximum number of items to keep in memory. This is useful when you want to browse an endless stream of data (e.g. log stream)
        with fzf while limiting memory usage."""
        return self.add(f"--tail={n}")

    no_tail = OptionsAdder("--no-tail")
    disable_search = OptionsAdder("--disabled")

    def tiebreak(self, *tiebreaks: Tiebreak) -> Self:
        """Comma-separated list of sort criteria to apply when the scores are tied.

        values:
            - length:   Prefers line with shorter length
            - chunk:    Prefers line with shorter matched chunk (delimited by whitespaces)
            - pathname: Prefers line with matched substring in the file name of the path
            - begin:    Prefers line with matched substring closer to the beginning
            - end:      Prefers line with matched substring closer to the end
            - index:    Prefers line that appeared earlier in the input stream
        """
        return self.add(f"--tiebreak={', '.join(tiebreaks)}")

    # INPUT/OUTPUT
    @property
    def read0(self) -> Self:
        """Read input delimited by ASCII NUL characters instead of newline characters.
        💡 Useful for multiline entries"""
        return self.add("--read0")

    @property
    def print0(self) -> Self:
        """Print output delimited by ASCII NUL characters instead of newline characters"""
        return self.add("--print0")

    no_read0 = OptionsAdder("--no-read0")
    no_print0 = OptionsAdder("--no-print0")
    ansi = OptionsAdder("--ansi")
    no_ansi = OptionsAdder("--no-ansi")
    sync = OptionsAdder("--sync")
    no_sync = OptionsAdder("--no-sync")
    no_tty_default = OptionsAdder("--no-tty-default")

    # GLOBAL STYLE
    def style(self, preset: str) -> Self:
        return self.add(f"--style={preset}")

    def color(self, color_options: str) -> Self:
        return self.add(f"--color={color_options}")

    no_color = OptionsAdder("--no-color")
    no_bold = OptionsAdder("--no-bold")
    black = OptionsAdder("--black")
    no_black = OptionsAdder("--no-black")

    # DISPLAY MODE
    def height(self, height_option: str) -> Self:
        return self.add(f"--height={height_option}")

    no_height = OptionsAdder("--no-height")

    def min_height(self, min_height_option: str) -> Self:
        return self.add(f"--min-height={min_height_option}")

    def tmux(self, tmux_option: str | None = None) -> Self:
        return self.add(f"--tmux={tmux_option}" if tmux_option is not None else "--tmux")

    no_tmux = OptionsAdder("--no-tmux")

    def layout(self, layout: Layout) -> Self:
        """
        values:
            - default: Display from the bottom of the screen
            - reverse: Display from the top of the screen
            - reverse-list: Display from the top of the screen, prompt at the bottom
        """
        return self.add(f"--layout={layout}")

    def margin(self, margin_option: str) -> Self:
        return self.add(f"--margin={margin_option}")

    def padding(self, padding_option: str) -> Self:
        return self.add(f"--padding={padding_option}")

    no_margin = OptionsAdder("--no-margin")
    no_padding = OptionsAdder("--no-padding")

    def border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--border={border}"]
        if label:
            args.append(f"--border-label={label}")
        return self.add(*args)

    def border_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--border-label-pos={position}")

    no_border = OptionsAdder("--no-border")
    no_border_label = OptionsAdder("--no-border-label")

    # LIST SECTION
    def multi(self, limit: int | None = None) -> Self:
        return self.add(f"--multi={limit}" if limit is not None else "--multi")

    no_multi = OptionsAdder("--no-multi")
    multiselect = OptionsAdder("--multi")
    highlight_line = OptionsAdder("--highlight-line")
    no_highlight_line = OptionsAdder("--no-highlight-line")
    cycle = OptionsAdder("--cycle")
    no_cycle = OptionsAdder("--no-cycle")
    wrap = OptionsAdder("--wrap")
    no_wrap = OptionsAdder("--no-wrap")

    def wrap_sign(self, indicator: str) -> Self:
        return self.add(f"--wrap-sign={indicator}")

    no_multi_line = OptionsAdder("--no-multi-line")
    track = OptionsAdder("--track")
    no_track = OptionsAdder("--no-track")

    @property
    def tac(self) -> Self:
        """Reverse the order of the input"""
        return self.add("--tac")

    no_tac = OptionsAdder("--no-tac")

    def gap(self, lines: int) -> Self:
        """Render empty lines between each item"""
        return self.add(f"--gap={lines}")

    def gap_line(self, line: str) -> Self:
        """The given string will be repeated to draw a horizontal line on each gap (default: '┈' or '-' depending on --no-unicode)."""
        return self.add(f"--gap-line={line}")

    no_gap = OptionsAdder("--no-gap")
    no_gap_line = OptionsAdder("--no-gap-line")
    keep_right = OptionsAdder("--keep-right")
    no_keep_right = OptionsAdder("--no-keep-right")

    def scroll_off(self, lines: int) -> Self:
        """Number of screen lines to keep above or below when scrolling to the top or to the bottom (default: 3)."""
        return self.add(f"--scroll-off={lines}")

    no_horizontal_scroll = OptionsAdder("--no-hscroll")

    def horizontal_scroll_off(self, columns: int) -> Self:
        """Number of screen columns to keep to the right of the highlighted substring (default: 10). Setting it to a large value will
        cause the text to be positioned on the center of the screen."""
        return self.add(f"--hscroll-off={columns}")

    def jump_labels(self, labels: str) -> Self:
        return self.add(f"--jump-labels={labels}")

    def pointer(self, pointer: str) -> Self:
        if len(pointer) > 2:
            raise ValueError(f"Pointer too long (should be max 2 chars): {pointer}")
        return self.add(f"--pointer={pointer}")

    def marker(self, marker: str) -> Self:
        if len(marker) > 2:
            raise ValueError(f"Marker too long (should be max 2 chars): {marker}")
        return self.add(f"--marker={marker}")

    def marker_multi_line(self, marker: str) -> Self:
        return self.add(f"--marker-multi-line={marker}")

    def ellipsis(self, ellipsis: str) -> Self:
        """Ellipsis to show when line is truncated (default: '··')"""
        return self.add(f"--ellipsis={ellipsis}")

    def tabstop(self, spaces: int) -> Self:
        return self.add(f"--tabstop={spaces}")

    def scrollbar(self, scrollbar_char: str, preview_scrollbar_char: str) -> Self:
        return self.add(f"--scrollbar={scrollbar_char}{preview_scrollbar_char}")

    no_scrollbar = OptionsAdder("--no-scrollbar")

    def list_border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--list-border={border}"]
        if label:
            args.append(f"--list-label={label}")
        return self.add(*args)

    def list_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--list-label-pos={position}")

    no_list_border = OptionsAdder("--no-list-border")
    no_list_label = OptionsAdder("--no-list-label")

    # INPUT SECTION
    no_input = OptionsAdder("--no-input")

    def prompt(self, prompt: str) -> Self:
        return self.add(f"--prompt={prompt}")

    def info(self, info: Info, prefix: str | None = None) -> Self:
        return self.add(f"--info={info}" + (f":{prefix}" if prefix else ""))

    def info_command(self, command: str) -> Self:
        return self.add(f"--info-command={command}")

    no_info = OptionsAdder("--no-info")
    no_info_command = OptionsAdder("--no-info-command")

    def separator(self, separator: str) -> Self:
        return self.add(f"--separator={separator}")

    no_separator = OptionsAdder("--no-separator")

    def ghost(self, ghost_text: str) -> Self:
        return self.add(f"--ghost={ghost_text}")

    filepath_word = OptionsAdder("--filepath-word")
    no_filepath_word = OptionsAdder("--no-filepath-word")

    def input_border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--input-border={border}"]
        if label:
            args.append(f"--input-label={label}")
        return self.add(*args)

    def input_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--input-label-pos={position}")

    no_input_border = OptionsAdder("--no-input-border")
    no_input_label = OptionsAdder("--no-input-label")

    # PREVIEW WINDOW
    def preview(self, command: str) -> Self:
        return self.add(f"--preview={command}")

    def preview_border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--preview-border={border}"]
        if label:
            args.append(f"--preview-label={label}")
        return self.add(*args)

    def preview_label(self, label: str) -> Self:
        return self.add(f"--preview-label={label}")

    def preview_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--preview-label-pos={position}")

    def preview_window(
        self, position: WindowPosition, size: int | RelativeWindowSize, *, line_wrap: bool = True
    ) -> Self:
        return self.add(f"--preview-window={position},{size}:{'wrap' if line_wrap else 'nowrap'}")

    no_preview = OptionsAdder("--no-preview")
    no_preview_border = OptionsAdder("--no-preview-border")
    no_preview_label = OptionsAdder("--no-preview-label")

    # HEADER
    def add_header(self, header: str) -> Self:
        self._header_strings.append(header)
        return self

    @property
    def header_option(self) -> str:
        return f"--header={'\n'.join(self._header_strings)}"

    def header_lines(self, count: int) -> Self:
        return self.add(f"--header-lines={count}")

    header_first = OptionsAdder("--header-first")
    no_header_first = OptionsAdder("--no-header-first")

    def header_border(self, border: Border, label: str | None = None, position: LabelPosition = "top") -> Self:
        args = [f"--header-border={border}"]
        if label:
            args.append(f"--header-label={label}")
            if position is not None:
                args.append(f"--header-label-pos={position}")
        return self.add(*args)

    def header_lines_border(self, border: Border) -> Self:
        return self.add(f"--header-lines-border={border}")

    no_header = OptionsAdder("--no-header")
    no_header_border = OptionsAdder("--no-header-border")
    no_header_label = OptionsAdder("--no-header-label")
    no_header_lines_border = OptionsAdder("--no-header-lines-border")
    no_header_lines = OptionsAdder("--no-header-lines")

    # FOOTER
    def add_footer(self, footer: str) -> Self:
        self._footer_strings.append(footer)
        return self

    @property
    def footer_option(self) -> str:
        return f"--footer={'\n'.join(self._footer_strings)}"

    def footer_border(self, border: Border, label: str | None = None, position: LabelPosition = "bottom") -> Self:
        args = [f"--footer-border={border}"]
        if label:
            args.append(f"--footer-label={label}")
            if position is not None:
                args.append(f"--footer-label-pos={position}")
        return self.add(*args)

    no_footer = OptionsAdder("--no-footer")
    no_footer_border = OptionsAdder("--no-footer-border")
    no_footer_label = OptionsAdder("--no-footer-label")

    # SCRIPTING
    def initial_query(self, query: str) -> Self:
        return self.add(f"--query={query}")

    select_1 = OptionsAdder("--select-1")
    exit_0 = OptionsAdder("--exit-0")
    no_exit_0 = OptionsAdder("--no-exit-0")

    def filter(self, query: str) -> Self:
        return self.add(f"--filter={query}")

    print_query = OptionsAdder("--print-query")
    no_print_query = OptionsAdder("--no-print-query")

    def expect(self, *hotkeys: Hotkey) -> Self:
        return self.add(f"--expect={','.join(hotkeys)}")

    no_expect = OptionsAdder("--no-expect")
    no_clear = OptionsAdder("--no-clear")

    # KEY/EVENT BINDINGS
    def bind(self, trigger: Hotkey | Event, action: str) -> Self:
        return self.add(f"--bind={trigger}:{action}")

    def bind_base_action(self, trigger: Hotkey | Event, action: BaseAction) -> Self:
        return self.bind(trigger, action)

    def bind_parametrized_action(self, trigger: Hotkey | Event, action: ParametrizedActionType, value: str) -> Self:
        return self.bind(trigger, f"{action}({value})")

    def bind_shell_command(
        self, trigger: Hotkey | Event, command: str, command_type: ShellCommandActionType = "execute"
    ) -> Self:
        return self.bind(trigger, f"{command_type}({command})")

    # ADVANCED
    def with_shell(self, interpreter: str) -> Self:
        return self.add(f"--with-shell={interpreter}")

    def listen(self, port_number: int = 0, unsafe: bool = False) -> Self:
        return self.add(f"--listen{'-unsafe' if unsafe else ''}={port_number}")

    no_listen = OptionsAdder("--no-listen")

    # DIRECTORY TRAVERSAL
    def walker(self, *walker_values: WalkerValue) -> Self:
        return self.add(f"--walker={','.join(walker_values)}")

    def walker_root(self, root_dir: str) -> Self:
        return self.add(f"--walker-root={root_dir}")

    def walker_skip(self, *paths: str) -> Self:
        return self.add(f"--walker-skip={','.join(paths)}")

    # HISTORY
    def history_file(self, path: str) -> Self:
        return self.add(f"--history={path}")

    def history_size(self, size: int) -> Self:
        return self.add(f"--history-size={size}")

    no_history = OptionsAdder("--no-history")

    # SHELL INTEGRATION
    pass

    # OTHERS
    no_mouse = OptionsAdder("--no-mouse")
    no_unicode = OptionsAdder("--no-unicode")
    ambidouble = OptionsAdder("--ambidouble")
    no_ambidouble = OptionsAdder("--no-ambidouble")

    # HELP
    pass

    # UTILITIES
    def __str__(self) -> str:
        return shlex.join(self)

    def __iter__(self):
        options = self.options.copy()
        if self._header_strings:
            options.append(self.header_option)
        if self._footer_strings:
            options.append(self.footer_option)
        return iter(options)

    def pretty(self) -> str:
        return "\n".join([shlex.quote(option) for option in self])

    def __add__(self, __other: Options) -> Self:
        options = self.add(*__other.options)
        options._header_strings += __other._header_strings
        options._footer_strings += __other._footer_strings
        return options

    # TODO: __sub__ for removing options?

    def __eq__(self, __other) -> bool:
        return (
            self.options == __other.options
            and self._header_strings == __other._header_strings
            and self._footer_strings == __other._footer_strings
        )
