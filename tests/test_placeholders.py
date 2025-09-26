from fzf_primitives import Prompt
from fzf_primitives.core.FzfPrompt.server import CommandOutput, FzfPlaceholder, VarOutput


def test_command_output():
    def function_with_command_output(prompt_data, command_output=CommandOutput("echo test")):
        prompt_data.obj = command_output

    prompt = Prompt(obj=[])
    prompt.mod.on_event().START.run_function("set command output", function_with_command_output, silent=True).accept()
    result = prompt.run()
    assert result.obj == "test"


def test_var_output():
    def function_with_var_output(prompt_data, action=VarOutput.preset.FZF_ACTION):
        prompt_data.obj.append(action)
        return action

    prompt = Prompt([1, 2, 3], obj=[])
    prompt.mod.options.multiselect()
    prompt.mod.preview().custom("set var output", function_with_var_output)
    prompt.mod.on_hotkey().CTRL_Q.accept()
    prompt.mod.automate_actions("up")
    prompt.mod.automate_actions("down")
    prompt.mod.automate_actions("down")
    prompt.mod.automate_actions("select")
    prompt.mod.automate("ctrl-q")
    result = prompt.run()
    assert result.obj == ["start", "up", "down", "down", "select"], f"Got {result.obj}"


def test_fzf_placeholders():
    def function_with_fzf_placeholders(
        prompt_data,
        matched_items_file=FzfPlaceholder.preset.MATCHED_ITEMS_FILE,
        current_index=FzfPlaceholder.preset.CURRENT_INDEX,
    ):
        with open(matched_items_file, "r") as f:
            placeholders = f.read().splitlines()
        prompt_data.obj["matched_items"] = placeholders
        prompt_data.obj["current_index"] = current_index

    prompt = Prompt([1, 2, 3], obj={})
    prompt.mod.on_hotkey().CTRL_6.run_function("set placeholders", function_with_fzf_placeholders, silent=True).accept()
    prompt.mod.automate("ctrl-6")
    result = prompt.run()
    assert result.obj["current_index"] == str(result.current_index)
    assert result.obj["matched_items"] == ["1", "2", "3"]


def get_placeholder_prompt():
    prompt = Prompt([1, 2, 3])
    mod = prompt.mod
    mod.preview("start", on_conflict="append").fzf_env_vars()
    mod.preview("ctrl-n", on_conflict="cycle with").fzf_placeholders()
    mod.preview("ctrl-n", on_conflict="cycle with").fzf_env_vars()

    return prompt


if __name__ == "__main__":
    get_placeholder_prompt().run()
