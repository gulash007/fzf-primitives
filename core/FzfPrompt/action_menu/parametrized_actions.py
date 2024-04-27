from ..options import BaseAction, ParametrizedActionType, ShellCommandActionType


class ParametrizedAction:

    def __init__(self, action_value: str, action_type: ParametrizedActionType) -> None:
        self.action_value = action_value
        self.action_type: ParametrizedActionType = action_type

    def action_string(self) -> str:
        return f"{self.action_type}({self.action_value})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.action_type}({self.action_value if len(self.action_value) < 20 else f'{self.action_value[:20]}...'})"


class ShellCommand(ParametrizedAction):
    def __init__(self, command: str, command_type: ShellCommandActionType = "execute") -> None:
        self.action_type: ShellCommandActionType
        super().__init__(command, command_type)

    @property
    def command(self) -> str:
        return self.action_value

    @property
    def command_type(self) -> ShellCommandActionType:
        return self.action_type


# Action can just be a string if you know what you're doing (look in `man fzf` for what can be assigned to '--bind')
Action = BaseAction | ParametrizedAction
