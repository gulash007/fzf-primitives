from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.monitoring import Logger
from ..main import Prompt
from .Recording import Recording

# TEST ALL KINDS OF STUFF
# TODO: test getting preview output
# TODO: test mods.on_event preset bindings chaining


def prompt_builder():
    prompt = Prompt(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    prompt.mod.options.multiselect
    prompt.mod.on_event("ctrl-a").toggle_all
    prompt.mod.on_event("ctrl-q").quit
    prompt.mod.preview("ctrl-h").basic
    prompt.mod.preview("ctrl-6").basic_indexed
    prompt.mod.preview("ctrl-y").custom(name="basic2", command="echo hello", window_size="50%", window_position="up")
    prompt.mod.on_event("ctrl-c").clip_current_preview.accept
    return prompt


if __name__ == "__main__":
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("TestPrompt", level="TRACE")
    recording = Recording(name="TestPrompt")
    recording.enable_logging()
    save_recording = False
    try:
        result = prompt_builder().run()
    except ExitLoop:
        pass
    else:
        recording.save_result(result)
        save_recording = True
        recording.save()
