from .core.FzfPrompt.options.events import Hotkey


class Config:
    logging_enabled: bool = True
    use_basic_hotkeys: bool = True
    default_accept_hotkey: Hotkey = "enter"
    default_abort_hotkey: Hotkey = "esc"
