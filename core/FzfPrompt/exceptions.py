# rename exception to signal its use to end prompt
class PromptEnd(Exception):
    ...


class ExitRound(PromptEnd):
    pass


class ExitLoop(PromptEnd):
    pass
