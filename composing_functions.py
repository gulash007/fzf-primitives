import functools
from pathlib import Path
import dill as pickle


def double(n: int):
    return 2 * n


def subtract_3(n: int):
    return n - 3


def composite_function(*functions):
    def compose(f, g):
        return lambda x: g(f(x))

    return functools.reduce(compose, functions, lambda x: x)


def compose(f, g):
    return lambda x: g(f(x))


# def compose(*functions):
#     def inner(arg):
#         for f in functions:
#             arg = f(arg)
#         return arg
#     return inner

FUNCTIONS = {"double": double, "subtract 3": subtract_3}

# func = compose(double, subtract_3)
# func = composite_function(double, subtract_3)
# import os
# PATH = Path("/Users/honza/Documents/Projects/PythonPackages/fzf-primitives/composite_functions/pickle.pkl")
# Path(os.path.dirname(PATH)).mkdir(parents=True, exist_ok=True)
# with open(PATH, "wb") as f:
#     pickle.dump(func, f)


# from pathlib import Path

# from pyfzf import FzfPrompt

# FUNCTION_STORAGE = Path("/Users/honza/Documents/Projects/PythonPackages/fzf-primitives/composite_functions/")
# mapping = {p.stem: p for p in FUNCTION_STORAGE.iterdir()}
# path = mapping[FzfPrompt().prompt(choices=mapping.keys())[0]]
# with open(path, "rb") as f:
#     obj = pickle.load(f)

# print(obj(4))
# print(obj(1))
# print(obj(5))
# print(obj(100))

import os

if __name__ == "__main__":
    from pyfzf import FzfPrompt

    def select_composition():
        function_names = []
        functions = []
        while True:
            key, function_name = FzfPrompt().prompt(choices=FUNCTIONS.keys(), fzf_options="--expect=ctrl-q")
            if key == "ctrl-q":
                break
            function_names.append(function_name)
            functions.append(FUNCTIONS[function_name])
        print(functions)
        return " ∘ ".join(reversed(function_names)), composite_function(*functions)

    function_name, func = select_composition()
    print(function_name)
    print(func(4))
    PATH = Path(
        f"/Users/honza/Documents/Projects/PythonPackages/fzf-primitives/composite_functions/{function_name}.pkl"
    )
    Path(os.path.dirname(PATH)).mkdir(parents=True, exist_ok=True)
    with open(PATH, "wb") as f:
        pickle.dump(func, f)
