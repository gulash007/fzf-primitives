from ..options import BaseAction, ParametrizedActionType, ShellCommandActionType


class ParametrizedAction:
    def __init__(self, action_value: str, action_type: ParametrizedActionType) -> None:
        self.action_value = action_value
        self._action_type: ParametrizedActionType = action_type

    @property
    def action_type(self) -> ParametrizedActionType:
        return self._action_type

    def action_string(self) -> str:
        return f"{self.action_type}({self.action_value})"

    def __str__(self) -> str:
        return f"[PA]{self.action_type}({self.action_value if len(self.action_value) < 20 else f'{self.action_value[:20]}...'})"


class CompositeAction:
    def __init__(self, *actions: BaseAction | ParametrizedAction) -> None:
        self.actions = actions

    def action_string(self) -> str:
        return "+".join(a.action_string() if isinstance(a, ParametrizedAction) else a for a in self.actions)

    def __str__(self) -> str:
        return f"[CA]({'+'.join(str(action) for action in self.actions)})"


class ShellCommand(ParametrizedAction):
    def __init__(self, command: str, command_type: ShellCommandActionType = "execute") -> None:
        self._command_type: ShellCommandActionType = command_type
        super().__init__(command, command_type)

    @property
    def action_type(self) -> ShellCommandActionType:
        return self._command_type

    @property
    def command(self) -> str:
        return self.action_value

    @property
    def command_type(self) -> ShellCommandActionType:
        return self._command_type

    def __str__(self) -> str:
        return f"[ShC]{self.action_type}({self.action_value if len(self.action_value) < 20 else f'{self.action_value[:20]}...'})"


class ChangeBorderLabel(ParametrizedAction):
    def __init__(self, label: str) -> None:
        super().__init__(label, "change-border-label")

    def __str__(self) -> str:
        return f"[CBL]({self.action_value})"


class MovePointer(ParametrizedAction):
    """❗ This conveniently converts indexing to 0-based like in Python.
    reasoning: fzf action pos(i) is 1-based, not 0-based, though it accepts negative values similar to Python.
    Also 0 is the same as 1. This means that pos(0) or pos(1) is the first item, pos(-1) is the last item.
    """

    def __init__(self, position: int) -> None:
        fzf_position_index = position + 1 if position >= 0 else position
        super().__init__(str(fzf_position_index), "pos")

    def __str__(self) -> str:
        return f"[pos]({self.action_value})"


class SelectAt(CompositeAction):
    def __init__(self, position: int):
        self._position = position
        super().__init__(MovePointer(position), "select")

    def __str__(self) -> str:
        return f"[SelAt]({self._position})"


class DeselectAt(CompositeAction):
    def __init__(self, position: int):
        self._position = position
        super().__init__(MovePointer(position), "deselect")

    def __str__(self) -> str:
        return f"[DeSelAt]({self._position})"


class ToggleAt(CompositeAction):
    def __init__(self, position: int):
        self._position = position
        super().__init__(MovePointer(position), "toggle")

    def __str__(self) -> str:
        return f"[TogAt]({self._position})"


class ToggleDownAt(CompositeAction):
    def __init__(self, position: int):
        self._position = position
        super().__init__(MovePointer(position), "toggle+down")

    def __str__(self) -> str:
        return f"[TogAtDw]({self._position})"


class ToggleUpAt(CompositeAction):
    def __init__(self, position: int):
        self._position = position
        super().__init__(MovePointer(position), "toggle+up")

    def __str__(self) -> str:
        return f"[TogAtUp]({self._position})"


# Action can just be a string if you know what you're doing (look in `man fzf` for what can be assigned to '--bind')
Action = BaseAction | ParametrizedAction | CompositeAction
