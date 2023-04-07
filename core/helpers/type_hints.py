from typing import Protocol, Generic, ParamSpec

from ..options import Options
from ..Prompt import Prompt
from ..MyFzfPrompt import Result


__all__ = ["Moddable", "P"]

P = ParamSpec("P")


class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt: Prompt, options: Options, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...
