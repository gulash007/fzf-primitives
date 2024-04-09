# rename exception to signal its use to end prompt
class ExpectedException(Exception):
    ...


class ExitRound(ExpectedException):
    pass


class ExitLoop(ExpectedException):
    pass
