from threading import Event, Thread

from fzf_primitives import Prompt
from fzf_primitives.actions import ParametrizedAction
from fzf_primitives.core.FzfPrompt import Binding
from fzf_primitives.core.FzfPrompt.controller import Controller
from fzf_primitives.core.monitoring import INTERNAL_LOG_DIR
from tests.LoggingSetup import LoggingSetup

logging_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_repeater")


@logging_setup.attach
def get_repeater():
    prompt = Prompt(["aaaaaaa"])
    prompt.mod.options.prompt("Type 'a's until nothing matches to trigger abort > ")

    prompt.mod.on_hotkey().CTRL_6.auto_repeat_run(
        "Repeat typing 'a'", ParametrizedAction("a", "put"), repeat_interval=0.1
    )
    prompt.mod.on_event().ZERO.abort
    prompt.mod.options.multiselect
    prompt.mod.on_event().MULTI.accept

    prompt.mod.automate("ctrl-6")
    return prompt


@logging_setup.attach
def test_repeater():
    prompt = get_repeater()

    thread_should_exit = Event()

    def stop_prompt_after_delay():
        if thread_should_exit.wait(2):
            return
        control_port = prompt._prompt_data._control_port
        if not control_port:
            print("❗ No control port found")
            return
        Controller().execute(control_port, Binding("", "select-all"))

    thread = Thread(target=stop_prompt_after_delay)
    thread.start()
    result = prompt.run()
    thread_should_exit.set()
    thread.join()
    assert result.end_status == "abort"


if __name__ == "__main__":
    get_repeater().run()
