import pytest

from .. import Prompt
from ..core.FzfPrompt.options import Options
from ..core.FzfPrompt.Prompt import BindingConflict
from ..core.mods import Mod, on_event, post_processing, preview


def test_mod_return_value_types():
    prompt = Prompt()

    # test chaining on_events
    assert type(prompt.mod.on_event("ctrl-a")) == on_event
    assert type(prompt.mod.on_event("ctrl-a").run("accept", "accept")) == on_event
    assert type(prompt.mod.on_event("ctrl-a").accept) == on_event
    assert type(prompt.mod.on_event("ctrl-o").open_files()) == on_event

    # test preview not being chainable
    assert type(prompt.mod.preview()) == preview
    assert prompt.mod.preview().custom("some preview", "echo hello") is None

    # test chaining post_processing
    assert type(prompt.mod.lastly) == post_processing
    assert type(prompt.mod.lastly.custom(lambda pd: None)) == post_processing
    assert type(prompt.mod.lastly.exit_round_on(lambda pd: True)) == post_processing
    assert type(prompt.mod.lastly.exit_round_when_aborted("Aborted!")) == post_processing

    # test chaining options
    assert type(prompt.mod.options) == Options
    assert type(prompt.mod.options.multiselect) == Options
    assert type(prompt.mod.options.multiselect.header("")) == Options

    # test mod presets
    assert type(prompt.mod.default) == Mod


def test_checking_for_event_conflicts():
    prompt = Prompt()
    with pytest.raises(BindingConflict):
        prompt.mod.on_event("ctrl-a").accept
        prompt.mod.on_event("ctrl-a").abort
        prompt.mod.apply()

    # clear mod
    prompt.mod.clear()
    assert len(prompt.mod._mods) == 0

    # no conflict
    ## override previous binding
    prompt.mod.on_event("ctrl-y").toggle_all.accept
    prompt.mod.on_event("ctrl-y", conflict_resolution="override").abort
    prompt.mod.on_event("ctrl-z").abort
    prompt.mod.apply()
    assert (
        prompt.mod._prompt_data.action_menu.bindings["ctrl-y"].name
        == prompt.mod._prompt_data.action_menu.bindings["ctrl-z"].name
    )

    ## append binding
    prompt.mod.on_event("ctrl-r").toggle
    prompt.mod.on_event("ctrl-r", conflict_resolution="append").select_all.accept
    prompt.mod.on_event("ctrl-s").toggle.select_all.accept
    prompt.mod.apply()
    assert (
        prompt.mod._prompt_data.action_menu.bindings["ctrl-r"].name
        == prompt.mod._prompt_data.action_menu.bindings["ctrl-s"].name
    )

    ## prepend binding
    prompt.mod.on_event("ctrl-b").accept
    prompt.mod.on_event("ctrl-b", conflict_resolution="prepend").toggle_preview.toggle_all
    prompt.mod.on_event("ctrl-n").toggle_preview.toggle_all.accept
    prompt.mod.apply()
    assert (
        prompt.mod._prompt_data.action_menu.bindings["ctrl-b"].name
        == prompt.mod._prompt_data.action_menu.bindings["ctrl-n"].name
    )
