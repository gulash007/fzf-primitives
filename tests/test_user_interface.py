import pytest

from .. import Prompt
from ..core.FzfPrompt import BindingConflict
from ..core.FzfPrompt.options import Options
from ..core.mods import Mod, OnEvent, PostProcessing, PreviewMod
from ..core.mods.EventAdder import HotkeyAdder, SituationAdder
from ..core.mods.preview_mod import PreviewMutationMod, PreviewMutationOnEvent


def test_mod_return_value_types():
    prompt = Prompt()

    # test chaining on_events
    assert type(prompt.mod.on_hotkey().CTRL_A) == OnEvent
    assert type(prompt.mod.on_situation().LOAD.run("toggle-all", "toggle-all")) == OnEvent
    assert type(prompt.mod.on_hotkey().CTRL_O.open_files()) == OnEvent
    ## except for .end_prompt
    assert prompt.mod.on_hotkey().CTRL_Q.end_prompt("accept", "accept") is None
    assert prompt.mod.on_hotkey().CTRL_C.accept is None

    # test preview modding
    assert type(prompt.mod.preview()) == PreviewMod
    assert type(prompt.mod.preview().custom("some preview", "echo hello")) == PreviewMutationMod
    assert type(prompt.mod.preview().custom("some preview", "echo hello").on_hotkey("ctrl-c")) == PreviewMutationOnEvent

    # test chaining post_processing
    assert type(prompt.mod.lastly) == PostProcessing
    assert type(prompt.mod.lastly.custom(lambda pd: None)) == PostProcessing
    assert type(prompt.mod.lastly.raise_aborted_on(lambda pd: True)) == PostProcessing
    assert type(prompt.mod.lastly.raise_from_aborted_status("Aborted!")) == PostProcessing

    # test chaining options
    assert type(prompt.mod.options) == Options
    assert type(prompt.mod.options.multiselect) == Options
    assert type(prompt.mod.options.multiselect.add_header("")) == Options

    # test mod presets
    assert type(prompt.mod.default) == Mod


def test_checking_for_event_conflicts():
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


def test_event_adder_usage():
    prompt = Prompt()

    assert type(prompt.mod.on_hotkey()) == HotkeyAdder
    assert type(prompt.mod.on_situation()) == SituationAdder
    assert type(prompt.mod.on_hotkey("ctrl-c")) == OnEvent
    assert type(prompt.mod.on_situation("one")) == OnEvent

    # used in PreviewMutationMod
    preview_mod = prompt.mod.preview()
    preview_mutation_mod = preview_mod.custom("some preview", "echo hello")
    assert type(preview_mutation_mod.on_hotkey()) == HotkeyAdder
    assert type(preview_mutation_mod.on_situation()) == SituationAdder
    assert type(preview_mutation_mod.on_hotkey("ctrl-c")) == PreviewMutationOnEvent
    assert type(preview_mutation_mod.on_situation("one")) == PreviewMutationOnEvent
