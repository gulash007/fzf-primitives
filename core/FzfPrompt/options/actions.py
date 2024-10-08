from typing import Literal

# raw fzf actions that aren't parametrized
BaseAction = Literal[
    "abort",
    "accept",
    "accept-non-empty",
    "accept-or-print-query",
    "backward-char",
    "backward-delete-char",
    "backward-delete-char/eof",
    "backward-kill-word",
    "backward-word",
    "beginning-of-line",
    "cancel",
    "clear-screen",
    "clear-selection",
    "close",
    "clear-query",
    "delete-char",
    "delete-char/eof",
    "deselect",
    "deselect-all",
    "disable-search",
    "down",
    "enable-search",
    "end-of-line",
    "first",
    "forward-char",
    "forward-word",
    "ignore",
    "jump",
    "jump-accept",
    "kill-line",
    "kill-word",
    "last",
    "next-history",
    "next-selected",
    "page-down",
    "page-up",
    "half-page-down",
    "half-page-up",
    "hide-header",
    "hide-preview",
    "offset-down",
    "offset-up",
    "prev-history",
    "prev-selected",
    "preview-down",
    "preview-up",
    "preview-page-down",
    "preview-page-up",
    "preview-half-page-down",
    "preview-half-page-up",
    "preview-bottom",
    "preview-top",
    "print-query",
    "refresh-preview",
    "replace-query",
    "select",
    "select-all",
    "show-header",
    "show-preview",
    "toggle",
    "toggle-all",
    "toggle+down",
    "toggle-header",
    "toggle-in",
    "toggle-out",
    "toggle-preview",
    "toggle-preview-wrap",
    "toggle-search",
    "toggle-sort",
    "toggle-track",
    "toggle+up",
    "track-current",
    "unix-line-discard",
    "unix-word-rubout",
    "untrack-current",
    "up",
    "yank",
]

# fzf actions that require an extra value
ParametrizedActionType = Literal[
    "become",  # TODO: Add this to ShellCommandActionType after you find use for it
    "change-border-label",
    "change-header",
    "change-preview",
    "change-preview-label",
    "change-preview-window",
    "change-prompt",
    "change-query",
    "execute",
    "execute-silent",
    "pos",
    "preview",
    "put",
    "rebind",
    "reload",
    "reload-sync",
    "transform",
    "transform-border-label",  # TODO: Add this to ShellCommandActionType after you find use for it
    "transform-header",  # TODO: Add this to ShellCommandActionType after you find use for it
    "transform-preview-label",  # TODO: Add this to ShellCommandActionType after you find use for it
    "transform-prompt",  # TODO: Add this to ShellCommandActionType after you find use for it
    "transform-query",  # TODO: Add this to ShellCommandActionType after you find use for it
    "unbind",
]

# those parametrized actions whose value is a shell command
ShellCommandActionType = Literal[
    "execute",
    "execute-silent",
    "change-preview",
    "change-prompt",
    "preview",
    "reload",
    "reload-sync",
    "transform",
]


# as per version 0.50.0 (brew)
FZF_ACTIONS = {
    "abort": "ctrl-c  ctrl-g  ctrl-q  esc",
    "accept": "enter   double-click",
    "accept-non-empty": "(same as accept except that it prevents fzf from exiting without selection)",
    "accept-or-print-query": "(same as accept except that it prints the query when there's no match)",
    "backward-char": "ctrl-b  left",
    "backward-delete-char": "ctrl-h  bspace",
    "backward-delete-char/eof": "(same as backward-delete-char except aborts fzf if query is empty)",
    "backward-kill-word": "alt-bs",
    "backward-word": "alt-b   shift-left",
    "become(...)": "(replace fzf process with the specified command; see below for the details)",
    "beginning-of-line": "ctrl-a  home",
    "cancel": "(clear query string if not empty, abort fzf otherwise)",
    "change-border-label(...)": "(change --border-label to the given string)",
    "change-header(...)": "(change header to the given string; doesn't affect --header-lines)",
    "change-preview(...)": "(change --preview option)",
    "change-preview-label(...)": "(change --preview-label to the given string)",
    "change-preview-window(...)": "(change --preview-window option; rotate through the multiple option sets separated by '|')",
    "change-prompt(...)": "(change prompt to the given string)",
    "change-query(...)": "(change query string to the given string)",
    "clear-screen": "ctrl-l",
    "clear-selection": "(clear multi-selection)",
    "close": "(close preview window if open, abort fzf otherwise)",
    "clear-query": "(clear query string)",
    "delete-char": "del",
    "delete-char/eof": "ctrl-d (same as delete-char except aborts fzf if query is empty)",
    "deselect": "",
    "deselect-all": "(deselect all matches)",
    "disable-search": "(disable search functionality)",
    "down": "ctrl-j  ctrl-n  down",
    "enable-search": "(enable search functionality)",
    "end-of-line": "ctrl-e  end",
    "execute(...)": "(see below for the details)",
    "execute-silent(...)": "(see below for the details)",
    "first": "(move to the first match; same as pos(1))",
    "forward-char": "ctrl-f  right",
    "forward-word": "alt-f   shift-right",
    "ignore": "",
    "jump": "(EasyMotion-like 2-keystroke movement)",
    "kill-line": "",
    "kill-word": "alt-d",
    "last": "(move to the last match; same as pos(-1))",
    "next-history": "(ctrl-n on --history)",
    "next-selected": "(move to the next selected item)",
    "page-down": "pgdn",
    "page-up": "pgup",
    "half-page-down": "",
    "half-page-up": "",
    "hide-header": "",
    "hide-preview": "",
    "offset-down": "(similar to CTRL-E of Vim)",
    "offset-up": "(similar to CTRL-Y of Vim)",
    "pos(...)": "(move cursor to the numeric position; negative number to count from the end)",
    "prev-history": "(ctrl-p on --history)",
    "prev-selected": "(move to the previous selected item)",
    "preview(...)": "(see below for the details)",
    "preview-down": "shift-down",
    "preview-up": "shift-up",
    "preview-page-down": "",
    "preview-page-up": "",
    "preview-half-page-down": "",
    "preview-half-page-up": "",
    "preview-bottom": "",
    "preview-top": "",
    "print-query": "(print query and exit)",
    "put": "(put the character to the prompt)",
    "put(...)": "(put the given string to the prompt)",
    "refresh-preview": "",
    "rebind(...)": "(rebind bindings after unbind)",
    "reload(...)": "(see below for the details)",
    "reload-sync(...)": "(see below for the details)",
    "replace-query": "(replace query string with the current selection)",
    "select": "",
    "select-all": "(select all matches)",
    "show-header": "",
    "show-preview": "",
    "toggle": "(right-click)",
    "toggle-all": "(toggle all matches)",
    "toggle+down": "ctrl-i  (tab)",
    "toggle-header": "",
    "toggle-in": "(--layout=reverse* ? toggle+up : toggle+down)",
    "toggle-out": "(--layout=reverse* ? toggle+down : toggle+up)",
    "toggle-preview": "",
    "toggle-preview-wrap": "",
    "toggle-search": "(toggle search functionality)",
    "toggle-sort": "",
    "toggle-track": "(toggle global tracking option (--track))",
    "toggle-track-current": "(toggle tracking of the current item)",
    "toggle+up": "btab    (shift-tab)",
    "track-current": "(track the current item; automatically disabled if focus changes)",
    "transform(...)": "(transform states using the output of an external command)",
    "transform-border-label(...)": "(transform border label using an external command)",
    "transform-header(...)": "(transform header using an external command)",
    "transform-preview-label(...)": "(transform preview label using an external command)",
    "transform-prompt(...)": "(transform prompt string using an external command)",
    "transform-query(...)": "(transform query string using an external command)",
    "unbind(...)": "(unbind bindings)",
    "unix-line-discard": "ctrl-u",
    "unix-word-rubout": "ctrl-w",
    "untrack-current": "(stop tracking the current item; no-op if global tracking is enabled)",
    "up": "ctrl-k  ctrl-p  up",
    "yank": "ctrl-y",
}
