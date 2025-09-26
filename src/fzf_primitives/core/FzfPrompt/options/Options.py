from __future__ import annotations

import shlex
from typing import Self

from .actions import BaseAction, ParametrizedActionType, ShellCommandActionType
from .triggers import Event, Hotkey
from .values import (
    Algorithm,
    Border,
    FzfOption,
    Info,
    LabelPosition,
    Layout,
    RelativeWindowSize,
    Scheme,
    Tiebreak,
    WalkerValue,
    WindowPosition,
)


class Options:
    def __init__(self, *fzf_options: FzfOption | str) -> None:
        self._options: list[str] = list(fzf_options)

    @property
    def options(self) -> list[str]:
        return self._options

    def add(self, *fzf_options: FzfOption | str) -> Self:
        self.options.extend(fzf_options)
        return self

    def get_indices_of(self, fzf_option: FzfOption | str, reverse: bool = False):
        for i, opt in reversed(list(enumerate(self._options))) if reverse else enumerate(self._options):
            if opt == fzf_option or opt.startswith(fzf_option + "="):
                yield i

    def get_index_of_last(self, fzf_option: FzfOption | str) -> int | None:
        return next(self.get_indices_of(fzf_option, reverse=True), None)

    def remove(self, fzf_option: FzfOption | str) -> Self:
        i = 0
        while i < len(self._options):
            opt = self._options[i]
            if opt == fzf_option:
                # Remove flag + its value (if any, and not another flag)
                del self._options[i]
                if i < len(self._options) and not self._options[i].startswith("--"):
                    del self._options[i]
            elif opt.startswith(fzf_option + "="):
                del self._options[i]
            else:
                i += 1
        return self

    def __str__(self) -> str:
        return shlex.join(self)

    def __iter__(self):
        return iter(self._options)

    def pretty(self) -> str:
        return " \\\n".join([shlex.quote(option) for option in self])

    def __add__(self, __other: Options) -> Self:
        self.add(*__other.options)
        return self

    def __eq__(self, __other) -> bool:
        return self.options == __other.options

    # SEARCH
    def extended(self) -> Self:
        return self.add("--extended")

    def no_extended(self) -> Self:
        return self.add("--no-extended")

    def exact(self) -> Self:
        return self.add("--exact")

    def no_exact(self) -> Self:
        return self.add("--no-exact")

    def ignore_case(self) -> Self:
        return self.add("--ignore-case")

    def no_ignore_case(self) -> Self:
        return self.add("--no-ignore-case")

    def smart_case(self) -> Self:
        return self.add("--smart-case")

    def literal(self) -> Self:
        return self.add("--literal")

    def no_literal(self) -> Self:
        return self.add("--no-literal")

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

    def sort(self) -> Self:
        return self.add("--sort")

    def no_sort(self) -> Self:
        return self.add("--no-sort")

    def delimiter(self, delimiter: str | None = None) -> Self:
        return self.add(f"--delimiter={delimiter}")

    def tail(self, n: int) -> Self:
        """Maximum number of items to keep in memory. This is useful when you want to browse an endless stream of data (e.g. log stream)
        with fzf while limiting memory usage."""
        return self.add(f"--tail={n}")

    def no_tail(self) -> Self:
        return self.add("--no-tail")

    def enabled(self) -> Self:
        return self.add("--enabled")

    def disabled(self) -> Self:
        return self.add("--disabled")

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
    def read0(self) -> Self:
        """Read input delimited by ASCII NUL characters instead of newline characters.
        💡 Useful for multiline entries"""
        return self.add("--read0")

    def print0(self) -> Self:
        """Print output delimited by ASCII NUL characters instead of newline characters"""
        return self.add("--print0")

    def no_read0(self) -> Self:
        return self.add("--no-read0")

    def no_print0(self) -> Self:
        return self.add("--no-print0")

    def ansi(self) -> Self:
        return self.add("--ansi")

    def no_ansi(self) -> Self:
        return self.add("--no-ansi")

    def sync(self) -> Self:
        return self.add("--sync")

    def no_sync(self) -> Self:
        return self.add("--no-sync")

    def tty_default(self, device_name: str) -> Self:
        return self.add(f"--tty-default={device_name}")

    def no_tty_default(self) -> Self:
        return self.add("--no-tty-default")

    # GLOBAL STYLE
    def style(self, preset: str) -> Self:
        return self.add(f"--style={preset}")

    def color(self, color_options: str) -> Self:
        return self.add(f"--color={color_options}")

    def no_color(self) -> Self:
        return self.add("--no-color")

    def no_256(self) -> Self:
        return self.add("--no-256")

    def bold(self) -> Self:
        return self.add("--bold")

    def no_bold(self) -> Self:
        return self.add("--no-bold")

    def black(self) -> Self:
        return self.add("--black")

    def no_black(self) -> Self:
        return self.add("--no-black")

    # DISPLAY MODE
    def height(self, height_option: str) -> Self:
        return self.add(f"--height={height_option}")

    def no_height(self) -> Self:
        return self.add("--no-height")

    def min_height(self, min_height_option: str) -> Self:
        return self.add(f"--min-height={min_height_option}")

    def tmux(self, tmux_option: str | None = None) -> Self:
        return self.add(f"--tmux={tmux_option}" if tmux_option is not None else "--tmux")

    def no_tmux(self) -> Self:
        return self.add("--no-tmux")

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

    def no_margin(self) -> Self:
        return self.add("--no-margin")

    def no_padding(self) -> Self:
        return self.add("--no-padding")

    def border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--border={border}"]
        if label:
            args.append(f"--border-label={label}")
        return self.add(*args)

    def border_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--border-label-pos={position}")

    def no_border(self) -> Self:
        return self.add("--no-border")

    def no_border_label(self) -> Self:
        return self.add("--no-border-label")

    # LIST SECTION
    def multi(self, limit: int | None = None) -> Self:
        return self.add(f"--multi={limit}" if limit is not None else "--multi")

    def no_multi(self) -> Self:
        return self.add("--no-multi")

    def highlight_line(self) -> Self:
        return self.add("--highlight-line")

    def no_highlight_line(self) -> Self:
        return self.add("--no-highlight-line")

    def cycle(self) -> Self:
        return self.add("--cycle")

    def no_cycle(self) -> Self:
        return self.add("--no-cycle")

    def wrap(self) -> Self:
        return self.add("--wrap")

    def no_wrap(self) -> Self:
        return self.add("--no-wrap")

    def wrap_sign(self, indicator: str) -> Self:
        return self.add(f"--wrap-sign={indicator}")

    def multi_line(self) -> Self:
        return self.add("--multi-line")

    def no_multi_line(self) -> Self:
        return self.add("--no-multi-line")

    def track(self) -> Self:
        return self.add("--track")

    def no_track(self) -> Self:
        return self.add("--no-track")

    def tac(self) -> Self:
        """Reverse the order of the input"""
        return self.add("--tac")

    def no_tac(self) -> Self:
        return self.add("--no-tac")

    def gap(self, lines: int) -> Self:
        """Render empty lines between each item"""
        return self.add(f"--gap={lines}")

    def gap_line(self, line: str) -> Self:
        """The given string will be repeated to draw a horizontal line on each gap (default: '┈' or '-' depending on --no-unicode)."""
        return self.add(f"--gap-line={line}")

    def no_gap(self) -> Self:
        return self.add("--no-gap")

    def no_gap_line(self) -> Self:
        return self.add("--no-gap-line")

    def keep_right(self) -> Self:
        return self.add("--keep-right")

    def no_keep_right(self) -> Self:
        return self.add("--no-keep-right")

    def scroll_off(self, lines: int) -> Self:
        """Number of screen lines to keep above or below when scrolling to the top or to the bottom (default: 3)."""
        return self.add(f"--scroll-off={lines}")

    def hscroll(self) -> Self:
        return self.add("--hscroll")

    def no_hscroll(self) -> Self:
        return self.add("--no-hscroll")

    def hscroll_off(self, columns: int) -> Self:
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

    def no_scrollbar(self) -> Self:
        return self.add("--no-scrollbar")

    def list_border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--list-border={border}"]
        if label:
            args.append(f"--list-label={label}")
        return self.add(*args)

    def list_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--list-label-pos={position}")

    def no_list_border(self) -> Self:
        return self.add("--no-list-border")

    def no_list_label(self) -> Self:
        return self.add("--no-list-label")

    # INPUT SECTION
    def no_input(self) -> Self:
        return self.add("--no-input")

    def prompt(self, prompt: str) -> Self:
        return self.add(f"--prompt={prompt}")

    def info(self, info: Info, prefix: str | None = None) -> Self:
        return self.add(f"--info={info}" + (f":{prefix}" if prefix else ""))

    def info_command(self, command: str) -> Self:
        return self.add(f"--info-command={command}")

    def no_info(self) -> Self:
        return self.add("--no-info")

    def no_info_command(self) -> Self:
        return self.add("--no-info-command")

    def separator(self, separator: str) -> Self:
        return self.add(f"--separator={separator}")

    def no_separator(self) -> Self:
        return self.add("--no-separator")

    def ghost(self, ghost_text: str) -> Self:
        return self.add(f"--ghost={ghost_text}")

    def filepath_word(self) -> Self:
        return self.add("--filepath-word")

    def no_filepath_word(self) -> Self:
        return self.add("--no-filepath-word")

    def input_border(self, border: Border, label: str | None = None) -> Self:
        args = [f"--input-border={border}"]
        if label:
            args.append(f"--input-label={label}")
        return self.add(*args)

    def input_label_pos(self, position: LabelPosition) -> Self:
        return self.add(f"--input-label-pos={position}")

    def no_input_border(self) -> Self:
        return self.add("--no-input-border")

    def no_input_label(self) -> Self:
        return self.add("--no-input-label")

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

    def no_preview(self) -> Self:
        return self.add("--no-preview")

    def no_preview_border(self) -> Self:
        return self.add("--no-preview-border")

    def no_preview_label(self) -> Self:
        return self.add("--no-preview-label")

    # HEADER
    def header(self, header: str) -> Self:
        return self.add(f"--header={header}")

    def add_header(self, extra: str, separator: str = "\n") -> Self:
        """Expects header to be assigned as --header=<value>, not separated into --header <value>"""
        if (index := self.get_index_of_last("--header")) is None:
            return self.header(extra)
        self.options[index] += f"{separator}{extra}"
        return self

    @property
    def header_option(self) -> str:
        if (index := self.get_index_of_last("--header")) is not None:
            return self.options[index].split("=", 1)[1]
        return ""

    def header_lines(self, count: int) -> Self:
        return self.add(f"--header-lines={count}")

    def header_first(self) -> Self:
        return self.add("--header-first")

    def no_header_first(self) -> Self:
        return self.add("--no-header-first")

    def header_border(self, border: Border, label: str | None = None, position: LabelPosition = "top") -> Self:
        args = [f"--header-border={border}"]
        if label:
            args.append(f"--header-label={label}")
            if position is not None:
                args.append(f"--header-label-pos={position}")
        return self.add(*args)

    def header_lines_border(self, border: Border) -> Self:
        return self.add(f"--header-lines-border={border}")

    def no_header(self) -> Self:
        return self.add("--no-header")

    def no_header_border(self) -> Self:
        return self.add("--no-header-border")

    def no_header_label(self) -> Self:
        return self.add("--no-header-label")

    def no_header_lines_border(self) -> Self:
        return self.add("--no-header-lines-border")

    def no_header_lines(self) -> Self:
        return self.add("--no-header-lines")

    # FOOTER
    def footer(self, footer: str) -> Self:
        return self.add(f"--footer={footer}")

    def add_footer(self, extra: str, separator: str = "\n") -> Self:
        """Expects footer to be assigned as --footer=<value>, not separated into --footer <value>"""
        if (index := self.get_index_of_last("--footer")) is None:
            return self.footer(extra)
        self.options[index] += f"{separator}{extra}"
        return self

    @property
    def footer_option(self) -> str:
        if (index := self.get_index_of_last("--footer")) is not None:
            return self.options[index].split("=", 1)[1]
        return ""

    def footer_border(self, border: Border, label: str | None = None, position: LabelPosition = "bottom") -> Self:
        args = [f"--footer-border={border}"]
        if label:
            args.append(f"--footer-label={label}")
            if position is not None:
                args.append(f"--footer-label-pos={position}")
        return self.add(*args)

    def no_footer(self) -> Self:
        return self.add("--no-footer")

    def no_footer_border(self) -> Self:
        return self.add("--no-footer-border")

    def no_footer_label(self) -> Self:
        return self.add("--no-footer-label")

    # SCRIPTING
    def query(self, query: str) -> Self:
        return self.add(f"--query={query}")

    def select_1(self) -> Self:
        return self.add("--select-1")

    def no_select_1(self) -> Self:
        return self.add("--no-select-1")

    def exit_0(self) -> Self:
        return self.add("--exit-0")

    def no_exit_0(self) -> Self:
        return self.add("--no-exit-0")

    def filter(self, query: str) -> Self:
        return self.add(f"--filter={query}")

    def print_query(self) -> Self:
        return self.add("--print-query")

    def no_print_query(self) -> Self:
        return self.add("--no-print-query")

    def expect(self, *hotkeys: Hotkey) -> Self:
        return self.add(f"--expect={','.join(hotkeys)}")

    def no_expect(self) -> Self:
        return self.add("--no-expect")

    def clear(self) -> Self:
        return self.add("--clear")

    def no_clear(self) -> Self:
        return self.add("--no-clear")

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

    def no_listen(self) -> Self:
        return self.add("--no-listen")

    # DIRECTORY TRAVERSAL
    def walker(self, *walker_values: WalkerValue) -> Self:
        return self.add(f"--walker={','.join(walker_values)}")

    def walker_root(self, root_dir: str) -> Self:
        return self.add(f"--walker-root={root_dir}")

    def walker_skip(self, *paths: str) -> Self:
        return self.add(f"--walker-skip={','.join(paths)}")

    # HISTORY
    def history(self, path: str) -> Self:
        return self.add(f"--history={path}")

    def history_size(self, size: int) -> Self:
        return self.add(f"--history-size={size}")

    def no_history(self) -> Self:
        return self.add("--no-history")

    # SHELL INTEGRATION
    pass

    # OTHERS
    def no_mouse(self) -> Self:
        return self.add("--no-mouse")

    def unicode(self) -> Self:
        return self.add("--unicode")

    def no_unicode(self) -> Self:
        return self.add("--no-unicode")

    def ambidouble(self) -> Self:
        return self.add("--ambidouble")

    def no_ambidouble(self) -> Self:
        return self.add("--no-ambidouble")

    # HELP
    pass
