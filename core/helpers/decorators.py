import functools
from typing import Callable, ParamSpec, TypeVar

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
