import pytest

from .. import Prompt
from ..core.FzfPrompt.options import Options
from ..core.mods import Mod, on_event, post_processing, preview, BindingConflict


def test_mod_return_value_types():
    prompt = Prompt()

    # test chaining on_events
    assert type(prompt.mod.on_event("ctrl-a").accept) == on_event
    assert type(prompt.mod.on_event("ctrl-o").open_files()) == on_event

    # test preview not being chainable
    assert type(prompt.mod.preview()) == preview
    assert prompt.mod.preview().basic is None

    # test chaining post_processing
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
