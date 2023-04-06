from typing import Protocol, TypeVar, Generic, ParamSpec

from ..options import Options
from ..Prompt import Prompt
from ..MyFzfPrompt import Result

P = ParamSpec("P")
R = TypeVar("R", bound=Result | Prompt, covariant=True)


class ModdableMethod(Protocol, Generic[P, R]):
    @staticmethod
    def __call__(self: Prompt, options: Options, *args: P.args, **kwargs: P.kwargs) -> R:
        ...
