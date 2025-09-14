from fzf_primitives.config import Config
from fzf_primitives.core.monitoring import Logger
from fzf_primitives.core.monitoring.constants import INTERNAL_LOG_DIR
from fzf_primitives.core.monitoring.LazyLogger import _DummyObject
from tests.LoggingSetup import LoggingSetup


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


def test_logging_setup():
    logging_enabled = Config.logging_enabled
    Config.logging_enabled = True
    try:
        local_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_monitoring1")
        different_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_monitoring2")

        @local_setup.attach
        def function_with_logging_setup():
            @local_setup.attach  # this is redundant but shouldn't cause issues
            def inner_function():
                handler_id = local_setup.handler_id
                assert handler_id in Logger.handlers()
                return handler_id

            @different_setup.attach
            def another_inner_function():
                handler_id = local_setup.handler_id
                different_handler_id = different_setup.handler_id
                assert handler_id != different_handler_id
                assert different_handler_id in Logger.handlers()
                assert handler_id in Logger.handlers()
                return handler_id

            handler_id = inner_function()
            assert handler_id == another_inner_function()
            assert local_setup.handler_id == handler_id
            assert handler_id in Logger.handlers()
            return handler_id

        handler_id = function_with_logging_setup()
        # after function completes, handler should be removed
        assert handler_id not in Logger.handlers()
    finally:
        Config.logging_enabled = logging_enabled
