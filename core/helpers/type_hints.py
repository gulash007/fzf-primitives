from typing import Protocol, Generic, ParamSpec

from ..intercom.PromptData import PromptData

from ..MyFzfPrompt import Result


__all__ = ["Moddable", "P"]

P = ParamSpec("P")


# TODO: compatibility with Typer? Or maybe modify Typer to accept it and ignore 'options'
class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...
