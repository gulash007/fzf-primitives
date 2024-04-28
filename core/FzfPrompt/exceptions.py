from ..FzfPrompt.prompt_data import Result


class PromptEnd(Exception):
    def __init__(self, message: str, result: Result) -> None:
        self.result = result
        super().__init__(message)


class Aborted(PromptEnd):
    pass


class Quitting(PromptEnd):
    pass
