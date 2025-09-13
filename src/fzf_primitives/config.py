import os

from .core.FzfPrompt.options.events import Hotkey

ENV_VAR_FOR_LOGGING = "FZF_PRIMITIVES_ENABLE_INTERNAL_LOGGING"


class Config:
    logging_enabled: bool = os.getenv(ENV_VAR_FOR_LOGGING, "0") == "1"
    use_basic_hotkeys: bool = True
    default_accept_hotkey: Hotkey = "enter"
    default_abort_hotkey: Hotkey = "esc"
