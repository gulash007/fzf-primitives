from typing import Callable, ParamSpec, TypeVar, Concatenate
from datetime import datetime

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

__all__ = ["single_use_method"]


def single_use_method(func: Callable[Concatenate[T, P], R]):
    def wrapped(self_or_cls: T, *args: P.args, **kwargs: P.kwargs) -> R:
        attr_name = f"_single_use_for_{id(self_or_cls)}"
        if not hasattr(self_or_cls, attr_name):
            setattr(self_or_cls, attr_name, {})
        if (memory := getattr(self_or_cls, attr_name)).get(func.__name__, None) is not None:
            raise RuntimeError(f"'.{func.__name__}' for {self_or_cls} already executed at {memory[func.__name__]}")
        memory[func.__name__] = datetime.now()
        return func(self_or_cls, *args, **kwargs)

    return wrapped
