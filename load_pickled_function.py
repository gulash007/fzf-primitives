import dill as pickle
from pathlib import Path

from pyfzf import FzfPrompt

FUNCTION_STORAGE = Path("/Users/honza/Documents/Projects/PythonPackages/fzf-primitives/composite_functions/")
mapping = {p.stem: p for p in FUNCTION_STORAGE.iterdir()}
path = mapping[FzfPrompt().prompt(choices=mapping.keys())[0]]
with open(path, "rb") as f:
    obj = pickle.load(f)


print(obj(4))
print(obj(1))
print(obj(5))
print(obj(100))
