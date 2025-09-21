import time

from fzf_primitives.core import Prompt
from fzf_primitives.core.FzfPrompt.server.actions import PromptEndingAction


def delayed_gen():
    for x in [4, 5]:
        time.sleep(0.2)
        yield x


def test_stream():
    entries = [1, 2, 3]
    prompt = Prompt(entries, entries_stream=delayed_gen())
    prompt.mod.options.multiselect

    prompt.mod.preview().fzf_json
    prompt.mod.on_hotkey().CTRL_N.run_shell_command("get total entries count", "echo $FZF_TOTAL_COUNT && read -n")
    prompt.mod.on_hotkey().CTRL_X.run_function("wait", lambda pd: time.sleep(3)).accept

    prompt.mod.on_event(on_conflict="append").RESULT.run_transform(
        "accept when there are 5 entries",
        lambda pd: ("toggle-all", PromptEndingAction("accept")) if len(pd.entries) == 5 else (),
    )

    result = prompt.run()
    assert result.selections == [1, 2, 3, 4, 5]


if __name__ == "__main__":
    test_stream()
