from .. import Prompt
from ..core.FzfPrompt.exceptions import ExitLoop
from ..core.FzfPrompt.prompt_data import PromptData
from ..core.monitoring import Logger
from .Recording import Recording

# TEST ALL KINDS OF STUFF
# TODO: test getting preview output
# TODO: test mods.on_event preset bindings chaining


def wait_for_input(prompt_data: PromptData[str, None]):
    input("Press Enter to continue...")


def bad_server_call_function(prompt_data: PromptData[int, str]): ...


def prompt_builder():
    prompt = Prompt(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    prompt.mod.options.multiselect
    prompt.mod.on_situation().BACKWARD_EOF.run_shell_command("clip socket number", "echo $SOCKET_NUMBER | clip")
    prompt.mod.on_hotkey().CTRL_A.toggle_all
    prompt.mod.on_hotkey().CTRL_Q.quit
    prompt.mod.on_hotkey().CTRL_C.clip_current_preview.accept
    prompt.mod.on_hotkey().CTRL_O.clip_options
    prompt.mod.on_hotkey().CTRL_N.run_function("wait", wait_for_input)
    # prompt.mod.on_hotkey().CTRL_X.run_function("wait", bad_server_call_function) # uncomment to reveal error
    prompt.mod.preview("ctrl-y").basic
    prompt.mod.preview("ctrl-6", "50%", "up").custom(name="basic2", command="echo {}", store_output=False)
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
