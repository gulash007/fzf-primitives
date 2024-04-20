from typing import Iterable

from ..options import BaseAction, ParametrizedActionType, ParametrizedOptionString, ShellCommandActionType


class ParametrizedAction(ParametrizedOptionString):

    def __init__(
        self, template: str, action_type: ParametrizedActionType, placeholders_to_resolve: Iterable[str] = ()
    ) -> None:
        self.action_type: ParametrizedActionType = action_type
        super().__init__(template, placeholders_to_resolve)

    def action_string(self) -> str:
        return f"{self.action_type}({self.resolved_string()})"


class ShellCommand(ParametrizedAction):
    def __init__(
        self,
        command_template: str,
        action_type: ShellCommandActionType = "execute",
        placeholders_to_resolve: Iterable[str] = (),
    ) -> None:
        super().__init__(command_template, action_type, placeholders_to_resolve)


# Action can just be a string if you know what you're doing (look in `man fzf` for what can be assigned to '--bind')
Action = BaseAction | ParametrizedAction
