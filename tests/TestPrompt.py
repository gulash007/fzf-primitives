from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.FzfPrompt.Prompt import PromptData, PromptEndingAction
from ..core.monitoring import Logger
from ..main import Prompt
from .Recording import Recording

# TEST ALL KINDS OF STUFF
# TODO: test getting preview output
# TODO: test mods.on_event preset bindings chaining


class ExitLoopWithoutSavingRecording(ExitLoop): ...


def quit_app_without_saving_recording(prompt_data: PromptData):
    raise ExitLoopWithoutSavingRecording


def prompt_builder():
    prompt = Prompt(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    prompt.mod.options.multiselect
    prompt.mod.on_event("ctrl-a").toggle_all
    prompt.mod.on_event("ctrl-q").quit
    prompt.mod.on_event("ctrl-n").run(
        "quit without saving recording", PromptEndingAction("abort", quit_app_without_saving_recording)
    )
    prompt.mod.preview("ctrl-h").basic
    prompt.mod.preview("ctrl-6").basic_indexed
    prompt.mod.preview("ctrl-y").custom(name="basic2", command="echo hello", window_size="50%", window_position="up")
    prompt.mod.on_event("ctrl-c").clip_current_preview.accept
    prompt.mod.lastly.exit_round_when_aborted("Aborted!")
    return prompt


if __name__ == "__main__":
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("TestPrompt", level="TRACE")
    recording = Recording(name="TestPrompt")
    recording.enable_logging()
    save_recording = True
    try:
        result = prompt_builder().run()
    except ExitLoop as e:
        if isinstance(e, ExitLoopWithoutSavingRecording):
            save_recording = False
    else:
        recording.save_result(result)
    if save_recording:
        recording.save()
