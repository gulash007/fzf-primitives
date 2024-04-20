import pytest

from .. import Prompt
from ..core.FzfPrompt import BindingConflict
from ..core.FzfPrompt.options import Options
from ..core.mods import Mod, OnEvent, PostProcessing, PreviewMod


def test_mod_return_value_types():
    prompt = Prompt()

    # test chaining on_events
    assert type(prompt.mod.on_hotkey().CTRL_A) == OnEvent
    assert type(prompt.mod.on_situation().LOAD.run("toggle-all", "toggle-all")) == OnEvent
    assert type(prompt.mod.on_hotkey().CTRL_O.open_files()) == OnEvent
    ## except for .end_prompt
    assert prompt.mod.on_hotkey().CTRL_Q.end_prompt("accept", "accept") is None
    assert prompt.mod.on_hotkey().CTRL_C.accept is None

    # test preview not being chainable
    assert type(prompt.mod.preview()) == PreviewMod
    assert prompt.mod.preview().custom("some preview", "echo hello") is None

    # test chaining post_processing
    assert type(prompt.mod.lastly) == PostProcessing
    assert type(prompt.mod.lastly.custom(lambda pd: None)) == PostProcessing
    assert type(prompt.mod.lastly.exit_round_on(lambda pd: True)) == PostProcessing
    assert type(prompt.mod.lastly.exit_round_when_aborted("Aborted!")) == PostProcessing

    # test chaining options
    assert type(prompt.mod.options) == Options
    assert type(prompt.mod.options.multiselect) == Options
    assert type(prompt.mod.options.multiselect.header("")) == Options

    # test mod presets
    assert type(prompt.mod.default) == Mod


def test_checking_for_event_conflicts():
    prompt = Prompt()
    with pytest.raises(BindingConflict):
        prompt.mod.on_hotkey().CTRL_A.accept
        prompt.mod.on_hotkey().CTRL_A.abort
        prompt.mod.apply()

    # clear mod
    prompt.mod.clear()
    assert len(prompt.mod._mods) == 0

    # no conflict
    ## override previous binding
    prompt.mod.on_hotkey().CTRL_Y.toggle_all.accept
    prompt.mod.on_hotkey(conflict_resolution="override").CTRL_Y.abort
    prompt.mod.on_hotkey().CTRL_Z.abort
    prompt.mod.apply()
    assert (
        prompt.mod._prompt_data.action_menu.bindings["ctrl-y"].name
        == prompt.mod._prompt_data.action_menu.bindings["ctrl-z"].name
    )

    ## append binding
    prompt.mod.on_hotkey().CTRL_R.toggle
    prompt.mod.on_hotkey(conflict_resolution="append").CTRL_R.select_all.accept
    prompt.mod.on_hotkey().CTRL_S.toggle.select_all.accept
    prompt.mod.apply()
    assert (
        prompt.mod._prompt_data.action_menu.bindings["ctrl-r"].name
        == prompt.mod._prompt_data.action_menu.bindings["ctrl-s"].name
    )

    ## prepend binding
    prompt.mod.on_hotkey().CTRL_B.accept
    prompt.mod.on_hotkey(conflict_resolution="prepend").CTRL_B.toggle_preview.toggle_all
    prompt.mod.on_hotkey().CTRL_N.toggle_preview.toggle_all.accept
    prompt.mod.apply()
    assert (
        prompt.mod._prompt_data.action_menu.bindings["ctrl-b"].name
        == prompt.mod._prompt_data.action_menu.bindings["ctrl-n"].name
    )
