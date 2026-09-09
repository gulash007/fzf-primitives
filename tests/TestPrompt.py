import sys

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not config_path:
        from . import TestPromptPlugin as TestPrompt
    else:
        from importlib import util

        spec = util.spec_from_file_location("TestPrompt", config_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load module from {config_path}")
        TestPrompt = util.module_from_spec(spec)
        spec.loader.exec_module(TestPrompt)

    prompt_builder = TestPrompt.prompt_builder
    prompt_builder().run()
