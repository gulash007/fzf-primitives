# TODO: Move it as presets to mods.preview?
class PREVIEW:
    basic = "python3.11 core/helper_cli_functions/preview_basic.py {q} {+}"

    @staticmethod
    def file(language: str) -> str:
        return f"python3.11 core/helper_cli_functions/preview_file.py {language} {{q}} {{+}}"
