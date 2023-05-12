class ACTION:
    select_all = "select-all"
    toggle_all = "toggle-all"

    @staticmethod
    def execute_silent(command: str) -> str:
        return f"execute-silent({command})"


class SHELL_COMMAND:
    clip_selections = "arr=({+}); printf '%s\\n' \"${arr[@]}\" | clip"
