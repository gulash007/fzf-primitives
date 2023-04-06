from typing import Callable, Protocol, TypeVar, Generic, ParamSpec

from ..options import Options
from ..Prompt import Prompt
from ..MyFzfPrompt import Result

P = ParamSpec("P")
R = TypeVar("R", bound=Result | Prompt, covariant=True)
AnyModdable = TypeVar("AnyModdable", bound="Moddable")


some_result = Result(["hello"])


class ModdableMethod(Protocol, Generic[P, R]):
    def __get__(self, obj, objtype=None) -> Callable[P, R]:
        ...

    @staticmethod
    def __call__(self_or_cls, /, *, options: Options) -> R:
        ...


class ModdableFunction(Protocol, Generic[P, R]):
    @staticmethod
    def __call__(*, options: Options) -> R:
        ...


Moddable = ModdableFunction | ModdableMethod
