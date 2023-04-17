from .intercom.PromptData import Preview

# TODO: Move it as presets to mods.preview?


class preview_constructor:
    def __init__(self, id, command):
        self._id = id
        self._command = command

    def __get__(self, obj, objtype=None):
        return Preview(id=self._id, command=self._command)


# log commands
class PREVIEW:
    basic = preview_constructor(
        id="basic",
        command="/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/.env/bin/python3.11 -m fzf_primitives.experimental.core.intercom.commands.get_preview %s 'basic'",
    )

    # @staticmethod
    # def file(language: str = "", theme: str = "") -> str:
    #     command = ["python3.11", "-m", "fzf_primitives.experimental.core.actions.view_file"]
    #     if language:
    #         command.extend(["--language", language])
    #     if theme:
    #         command.extend(["--theme", theme])
    #     return f"{shlex.join(command)} -- {{q}} {{+}}"
