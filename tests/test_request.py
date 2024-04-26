from ..core.FzfPrompt.server import Request
import functools


def test_handling_partial_functions():
    def func(prompt_data, p1, p2): ...

    params = Request.parse_function_parameters(functools.partial(func, p2="arg2"))
    assert [p.name for p in params] == ["p1"]
