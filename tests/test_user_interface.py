import pytest

from fzf_primitives import Prompt
from fzf_primitives.core.FzfPrompt import BindingConflict
from fzf_primitives.core.FzfPrompt.options import Options
from fzf_primitives.core.mods import Mod, OnTrigger, PostProcessing, PreviewMod
from fzf_primitives.core.mods.trigger_adder.TriggerAdder import HotkeyAdder, EventAdder
from fzf_primitives.core.mods.preview_mod import SpecificPreviewMod, SpecificPreviewOnTrigger

# ruff: noqa: SLF001

def test_mod_return_value_types():
    prompt = Prompt()

    # test chaining on_triggers
    assert type(prompt.mod.on_hotkey().CTRL_A) is OnTrigger
    assert type(prompt.mod.on_event().LOAD.run("toggle-all", "toggle-all")) is OnTrigger
    assert type(prompt.mod.on_hotkey().CTRL_O.open_files()) is OnTrigger
    ## except for .end_prompt
    assert prompt.mod.on_hotkey().CTRL_Q.end_prompt("accept", "accept") is None
    assert prompt.mod.on_hotkey().CTRL_C.accept is None

    # test preview modding
    assert type(prompt.mod.preview()) is PreviewMod
    assert type(prompt.mod.preview().custom("some preview", "echo hello")) is SpecificPreviewMod
    assert type(prompt.mod.preview().custom("some preview", "echo hello").on_hotkey("ctrl-c")) is SpecificPreviewOnTrigger

    # test chaining post_processing
    assert type(prompt.mod.lastly) is PostProcessing
    assert type(prompt.mod.lastly.custom(lambda pd: None)) is PostProcessing
    assert type(prompt.mod.lastly.raise_aborted_on(lambda pd: True)) is PostProcessing
    assert type(prompt.mod.lastly.raise_from_aborted_status("Aborted!")) is PostProcessing

    # test chaining options
    assert type(prompt.mod.options) is Options
    assert type(prompt.mod.options.multiselect) is Options
    assert type(prompt.mod.options.multiselect.add_header("")) is Options

    # test mod presets
    assert type(prompt.mod.default) is Mod


def test_checking_for_trigger_conflicts():
    prompt = Prompt()
    with pytest.raises(BindingConflict):
        prompt.mod.on_hotkey().CTRL_A.accept
        prompt.mod.on_hotkey().CTRL_A.abort
        prompt.mod.apply(prompt._prompt_data)

    # clear mod
    prompt.mod.clear()
    assert len(prompt.mod._mods) == 0

    # no conflict
    ## override previous binding
    prompt.mod.on_hotkey().CTRL_Y.toggle_all.accept
    prompt.mod.on_hotkey(on_conflict="override").CTRL_Y.abort
    prompt.mod.on_hotkey().CTRL_Z.abort
    prompt.mod.apply(prompt._prompt_data)
    assert (
        prompt._prompt_data.action_menu.bindings["ctrl-y"].name
        == prompt._prompt_data.action_menu.bindings["ctrl-z"].name
    )

    ## append binding
    prompt.mod.on_hotkey().CTRL_R.toggle
    prompt.mod.on_hotkey(on_conflict="append").CTRL_R.select_all.accept
    prompt.mod.on_hotkey().CTRL_S.toggle.select_all.accept
    prompt.mod.apply(prompt._prompt_data)
    assert (
        prompt._prompt_data.action_menu.bindings["ctrl-r"].name
        == prompt._prompt_data.action_menu.bindings["ctrl-s"].name
    )

    ## prepend binding
    prompt.mod.on_hotkey().CTRL_B.accept
    prompt.mod.on_hotkey(on_conflict="prepend").CTRL_B.toggle_preview.toggle_all
    prompt.mod.on_hotkey().CTRL_N.toggle_preview.toggle_all.accept
    prompt.mod.apply(prompt._prompt_data)
    assert (
        prompt._prompt_data.action_menu.bindings["ctrl-b"].name
        == prompt._prompt_data.action_menu.bindings["ctrl-n"].name
    )


def test_trigger_adder_usage():
    prompt = Prompt()

    assert type(prompt.mod.on_hotkey()) is HotkeyAdder
    assert type(prompt.mod.on_event()) is EventAdder
    assert type(prompt.mod.on_hotkey("ctrl-c")) is OnTrigger
    assert type(prompt.mod.on_event("one")) is OnTrigger

    # used in PreviewMutationMod
    preview_mod = prompt.mod.preview()
    preview_mutation_mod = preview_mod.custom("some preview", "echo hello")
    assert type(preview_mutation_mod.on_hotkey()) is HotkeyAdder
    assert type(preview_mutation_mod.on_event()) is EventAdder
    assert type(preview_mutation_mod.on_hotkey("ctrl-c")) is SpecificPreviewOnTrigger
    assert type(preview_mutation_mod.on_event("one")) is SpecificPreviewOnTrigger
