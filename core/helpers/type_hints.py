from __future__ import annotations

from typing import Generic, ParamSpec, Protocol, TypeVar

from ..ActionMenu import ActionMenu
from ..DefaultPrompt import DefaultPrompt
from ..MyFzfPrompt import Result
from ..options import Options

P = ParamSpec("P")
AnyPrompt = TypeVar("AnyPrompt", bound="Prompt")


class Prompt(Protocol):
    run: ModdableMethod


class ModdableMethod(Protocol, Generic[P]):
    @staticmethod
    def __call__(self: Prompt, options: Options = Options(), *args: P.args, **kwargs: P.kwargs) -> Result:
        ...


am = ActionMenu()


@am
def run(self: DefaultPrompt, options: Options = Options(), name: str = "bot"):
    return Result([])
