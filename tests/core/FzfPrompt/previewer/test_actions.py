import subprocess

import pytest

from fzf_primitives.core.FzfPrompt.previewer.actions import ChangePreviewWindow


@pytest.mark.parametrize("line_wrap", [True, False, None])
@pytest.mark.parametrize("window_position", ["left", None])
@pytest.mark.parametrize("window_size", [None, 0, 100, "50%"])
def test_change_preview_window(window_size, window_position, line_wrap):
    action = ChangePreviewWindow(window_size=window_size, window_position=window_position, line_wrap=line_wrap)
    result = subprocess.run(["fzf", "--version", f"--bind=ctrl-p:{action.action_string()}"], stdout=subprocess.PIPE)
    assert result.returncode == 0
