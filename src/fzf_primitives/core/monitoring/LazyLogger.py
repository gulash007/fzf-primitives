from typing import TYPE_CHECKING

from ... import config

if TYPE_CHECKING:
    from ._Logger import add_file_handler, get_logger, remove, remove_preset_handlers

__all__ = ["get_logger", "remove_preset_handlers", "remove", "add_file_handler"]


_dynamic_imports = {
    "get_logger": (__package__, "._Logger"),
    "remove": (__package__, "._Logger"),
    "remove_preset_handlers": (__package__, "._Logger"),
    "add_file_handler": (__package__, "._Logger"),
}


def __getattr__(attr_name: str) -> object:
    if not config.Config.logging_enabled:
        return _DummyObject()

    from importlib import import_module

    dynamic_attr = _dynamic_imports[attr_name]
    package, module_name = dynamic_attr
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
