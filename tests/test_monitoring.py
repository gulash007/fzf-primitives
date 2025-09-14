from fzf_primitives.config import Config
from fzf_primitives.core.monitoring import Logger
from fzf_primitives.core.monitoring.LazyLogger import _DummyObject


def test_lazy_logging():
    logging_enabled = Config.logging_enabled
    Config.logging_enabled = False
    try:
        assert isinstance(Logger.remove_preset_handlers(), _DummyObject)
        assert isinstance(Logger.remove(), _DummyObject)
        assert isinstance(Logger.add_file_handler("some_path.log"), _DummyObject)
        assert isinstance(Logger.get_logger(), _DummyObject)
    finally:
        Config.logging_enabled = logging_enabled


def test_remove_preset_handlers():
    Config.logging_enabled = True
    try:
        # should be able to call multiple times without error
        Logger.remove_preset_handlers()
        Logger.remove_preset_handlers()
    finally:
        Config.logging_enabled = False
