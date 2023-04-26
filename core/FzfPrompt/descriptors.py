from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def preset(cls: Callable[P, T]) -> Callable[P, T]:
    """Ensures that a new instance of cls is created from accessing the descriptor"""

    def get_new_instance(*args: P.args, **kwargs: P.kwargs) -> T:
        class presetter_descriptor:
            def __get__(self, obj, objtype=None) -> T:
                return cls(*args, **kwargs)

        return presetter_descriptor()  # type: ignore

    return get_new_instance
