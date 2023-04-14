import functools
import typer
from typing import Any, Optional, Protocol
from ..helpers.decorators import output_to_stdin_and_return


class Action(Protocol):
    @staticmethod
    def __call__(query: str, selections: list[str]) -> Any:
        pass


class ActionSupportingIndices(Protocol):
    @staticmethod
    def __call__(query: str, selections: list[str], indices: Optional[list[int]] = None) -> Any:
        pass


with_indices_help = """With this option, the first half of selections are interpreted as the actual selections
and the other half are interpreted as their indices"""

EMPTY_SELECTION = [""]  # when there's no selection and {} or {+} in fzf is passed as selections


def supports_indexed_selections(action: ActionSupportingIndices):
    """Ignores empty selection so that {q} {+} with empty selection (due to query not matching anything)
    isn't interpreted as list with an empty string instead of an empty list. {+n} isn't passed as an empty string
    curiously"""

    def supporting_indexed_selections(
        query: str, selections: list[str], with_indices: bool = typer.Option(False, help=with_indices_help)
    ):
        if selections == EMPTY_SELECTION:
            selections = []
        if not with_indices:
            return action(query, selections)
        length = len(selections)
        if length % 2 != 0:
            raise ValueError(f"Odd number of selections passed with --with-indices option: {selections}")
        middle_index = length // 2
        indices = selections[middle_index:]
        try:
            indices = list(map(int, indices))
        except ValueError:
            raise ValueError(f"Supposed indices aren't all integers: {indices}")
        actual_selections = selections[:middle_index]
        return action(query, actual_selections, indices)

    return supporting_indexed_selections


class CommandCreator(typer.Typer):
    @property
    def register_command(self):
        @functools.wraps(self.command)
        def wrapper(*args, **kwargs):
            def registering_command(func: Action):
                self.command(*args, **kwargs)(output_to_stdin_and_return(func))
                return func

            return registering_command

        return wrapper

    @property
    def register_command_supporting_indices(self):
        @functools.wraps(self.command)
        def wrapper(*args, **kwargs):
            def registering_command(func: ActionSupportingIndices):
                self.command(*args, **kwargs)(output_to_stdin_and_return(func))
                return func

            return registering_command

        return wrapper
