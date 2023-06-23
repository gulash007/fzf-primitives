import functools
from typing import Callable, ParamSpec, TypeVar, Concatenate
from datetime import datetime

P = ParamSpec("P")
R = TypeVar("R")

__all__ = ["output_to_stdin_and_return"]


def output_to_stdin_and_return(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def function_whose_return_value_should_be_printed(*args: P.args, **kwargs: P.kwargs) -> R:
        value = func(*args, **kwargs)
        print(value)
        return value

    return function_whose_return_value_should_be_printed


def constructor(cls: Callable[P, R]) -> Callable[P, R]:
    """Meant to be used with functools.partial to create partial constructors.
    Motivation is that functools.partial(SomeClass, ...) doesn't propagate parameter hints correctly"""

    def construct(*args: P.args, **kwargs: P.kwargs) -> R:
        return cls(*args, **kwargs)

    return construct


T = TypeVar("T")


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
