import itertools
from typing import Any, Callable, Iterable, Mapping


class MultiDimensionalGenerator[T]:
    def __init__(
        self, mutation_dict: Mapping[Any, Callable | Iterable], get_result: Callable[..., T] = lambda *args: args
    ):
        self.mutation_dict: dict[Any, dict] = {}
        for key, value in mutation_dict.items():
            if callable(value):
                self.mutation_dict[key] = {"function": value, "result": value()}
            else:
                next_in_cycle = self.get_cycler(value)
                self.mutation_dict[key] = {"function": next_in_cycle, "result": next_in_cycle()}
        self.result_calculator = get_result

    def next(self, key) -> T:
        self.mutation_dict[key]["result"] = self.mutation_dict[key]["function"]()
        return self.current_result()

    def current_result(self) -> T:
        return self.result_calculator(*(obj["result"] for obj in self.mutation_dict.values()))

    @staticmethod
    def get_cycler(values):
        cycle = itertools.cycle(values)
        return lambda: next(cycle)
