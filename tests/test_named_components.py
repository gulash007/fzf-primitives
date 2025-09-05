from fzf_primitives.core.FzfPrompt.action_menu.parametrized_actions import ParametrizedAction
from fzf_primitives.core.FzfPrompt.action_menu.binding import Binding
from fzf_primitives.core.FzfPrompt.action_menu.transform import Transform
from fzf_primitives.core.FzfPrompt.server import ServerCall, PromptEndingAction
from fzf_primitives.core.FzfPrompt.previewer.Preview import Preview
from fzf_primitives.actions import (
    ShellCommand,
    ChangeBorderLabel,
    ChangePreviewLabel,
    ChangePreviewWindow,
    ShowAndStorePreviewOutput,
    SetAsCurrentPreview,
    ReloadChoices,
)


def get_names_when_using_lambdas():
    binding = Binding(
        None,
        ShellCommand("echo hello", "execute-silent"),
        ServerCall(lambda pd: "output"),
        Transform(lambda pd: [ParametrizedAction("echo hello", "become")]),
        *Preview("Some preview", output_generator=lambda pd: "some preview output").preview_change_binding.actions,
        PromptEndingAction("accept", "alt-0", lambda pd: None),
    )
    print("----- test_names_when_using_lambdas -----")
    print("binding.name:", binding.name)
    print("str(binding):", binding)


def get_names_when_using_named_functions():
    def get_output(prompt_data):
        return "output"

    def get_become_echo_hello(prompt_data):
        return [ParametrizedAction("echo hello", "become")]

    def get_some_preview_output(prompt_data):
        return "some preview output"

    def post_processor_that_does_nothing(prompt_data):
        pass

    binding = Binding(
        None,
        ShellCommand("echo hello", "execute-silent"),
        ServerCall(get_output),
        Transform(get_become_echo_hello),
        *Preview("Some preview", output_generator=get_some_preview_output).preview_change_binding.actions,
        PromptEndingAction("accept", "alt-0", post_processor_that_does_nothing),
    )
    print("----- test_names_when_using_named_functions -----")
    print("binding.name:", binding.name)
    print("str(binding):", binding)


def get_names_when_assigning_custom_names():
    binding = Binding(
        "Some binding",
        ShellCommand("echo hello", "execute-silent"),
        ServerCall(lambda pd: "output", "Getting server call output"),
        Transform(lambda pd: [ParametrizedAction("echo hello", "become")], "Become echo hello"),
        *Preview("Some preview", output_generator=lambda pd: "some preview output").preview_change_binding.actions,
        PromptEndingAction("accept", "alt-0", lambda pd: None),
    )
    print("----- test_names_when_assigning_custom_names -----")
    print("binding.name:", binding.name)
    print("str(binding):", binding)


if __name__ == "__main__":
    get_names_when_using_lambdas()
    get_names_when_using_named_functions()
    get_names_when_assigning_custom_names()
