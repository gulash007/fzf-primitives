from fzf_primitives import Prompt
from fzf_primitives.core.FzfPrompt.server.actions import ServerCall
from fzf_primitives.core.monitoring import INTERNAL_LOG_DIR
from tests.LoggingSetup import LoggingSetup

logging_setup = LoggingSetup(INTERNAL_LOG_DIR / "test_automator")


@logging_setup.attach
def test_automating_hotkeys():
    prompt = Prompt([1, 2])
    prompt.mod.options.multi()
    prompt.mod.on_hotkey("ctrl-a").select_all()
    prompt.mod.automate("ctrl-a")
    prompt.mod.automate(prompt.config.default_accept_hotkey)

    result = prompt.run()
    assert result.selections == [1, 2], f"Unexpected selections: {result.selections}"


@logging_setup.attach
def test_automating_actions():
    prompt = Prompt([1, 2, 3, 4])
    prompt.mod.options.multi()
    prompt.mod.automate_actions("select", "down", "select", "down", "select")
    prompt.mod.automate(prompt.config.default_accept_hotkey)

    result = prompt.run()
    assert result.selections == [1, 2, 3], f"Unexpected selections: {result.selections}"


@logging_setup.attach
def test_automating_server_call():
    prompt = Prompt([1, 2, 3], obj=[])
    prompt_data = prompt._prompt_data  # noqa: SLF001
    prompt.mod.apply(prompt_data)
    prompt_data.automator.automate_actions(ServerCall(lambda pd: pd.obj.append(4)))
    prompt_data.automator.automate(prompt.config.default_accept_hotkey)

    result = prompt.run()
    assert result.obj == [4]
