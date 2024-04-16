from .options import Hotkey

DEFAULT_ACCEPT_HOTKEY: Hotkey = "enter"
DEFAULT_ABORT_HOTKEY: Hotkey = "esc"


class SHELL_COMMAND:
    clip_selections = "arr=({+}); printf '%s\\n' \"${arr[@]}\" | clip"
