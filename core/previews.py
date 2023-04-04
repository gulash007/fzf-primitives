# TODO: Move it as presets to mods.preview?
from pathlib import Path
from typing import Optional


class PREVIEW:
    basic = "python3.11 -m fzf_primitives.core.helper_cli_functions.preview_basic {q} {+}"

    @staticmethod
    def file(language: str = "", theme: str = "", directory: Optional[Path] = None) -> str:
        directory_arg = f"--directory {directory}" if directory else ""
        language_arg = f"--language {language}" if language else ""
        theme_arg = f'--theme "{theme}"' if theme else ""
        return f"python3.11 -m fzf_primitives.core.helper_cli_functions.preview_file {{q}} {{+}} {directory_arg} {language_arg} {theme_arg}"
