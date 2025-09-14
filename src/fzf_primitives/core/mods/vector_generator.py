import itertools
from typing import Any, Callable, Iterable, Mapping


class VectorGenerator[K, T]:
    def __init__(
        self, dimensions: Mapping[K, Callable[[], Any] | Iterable], get_result: Callable[..., T] = lambda *args: args
    ):
        self.dimensions: dict[Any, dict] = {}
        for dimension_name, value_getter in dimensions.items():
            if callable(value_getter):
                self.dimensions[dimension_name] = {"function": value_getter, "result": value_getter()}
            else:
                next_in_cycle = self.get_cycler(value_getter)
                self.dimensions[dimension_name] = {"function": next_in_cycle, "result": next_in_cycle()}
        self.get_result = get_result

    def next(self, dimension_name: K) -> T:
        self.dimensions[dimension_name]["result"] = self.dimensions[dimension_name]["function"]()
        return self.current_result()

    def current_result(self) -> T:
        return self.get_result(*(obj["result"] for obj in self.dimensions.values()))

    @staticmethod
    def get_cycler(values):
        cycle = itertools.cycle(values)
        return lambda: next(cycle)
