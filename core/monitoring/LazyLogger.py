from typing import TYPE_CHECKING
from ... import config

if TYPE_CHECKING:
    from ._Logger import get_logger, remove_handler, add_file_handler, clear_log_file

__all__ = ["get_logger", "remove_handler", "add_file_handler", "clear_log_file"]

# type: ignore


_dynamic_imports = {
    "get_logger": (__package__, "._Logger"),
    "remove_handler": (__package__, "._Logger"),
    "add_file_handler": (__package__, "._Logger"),
    "clear_log_file": (__package__, "._Logger"),
}


def __getattr__(attr_name: str) -> object:
    dynamic_attr = _dynamic_imports[attr_name]
    package, module_name = dynamic_attr

    from importlib import import_module

    if not config.Config.logging_enabled:
        return _DummyObject()
    module = import_module(module_name, package=package)
    return getattr(module, attr_name)


class _DummyObject:
    def __getattr__(self, name):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __setitem__(self, key, item):
        pass

    def __getitem__(self, key):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def __len__(self):
        return 0

    def __contains__(self, item):
        return False

    def __bool__(self):
        return False
