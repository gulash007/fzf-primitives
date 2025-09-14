import os

from .core.FzfPrompt.options.triggers import Hotkey

ENV_VAR_FOR_LOGGING = "FZF_PRIMITIVES_ENABLE_INTERNAL_LOGGING"
ENV_VAR_FOR_AUTOMATOR_DELAY = "FZF_PRIMITIVES_AUTOMATOR_DELAY"


class Config:
    logging_enabled: bool = os.getenv(ENV_VAR_FOR_LOGGING, "0") == "1"
    use_basic_hotkeys: bool = True
    default_accept_hotkey: Hotkey = "enter"
    default_abort_hotkey: Hotkey = "esc"

    automator_delay: float = float(os.getenv(ENV_VAR_FOR_AUTOMATOR_DELAY, "0.25"))
