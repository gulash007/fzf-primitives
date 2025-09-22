import subprocess
from typing import get_args

from fzf_primitives.core.FzfPrompt.options import Options
from fzf_primitives.core.FzfPrompt.options.values import FzfOption


def test_options_comparisons():
    assert Options("--ansi") == Options("--ansi")
    assert Options("--ansi", "--no-sort") == Options("--ansi", "--no-sort")
    assert Options("--ansi") != Options("--ansi", "--no-sort")

    assert Options("--ansi") + Options("--no-sort") == Options("--ansi", "--no-sort")

    assert Options("--ansi") == Options().ansi

    assert Options().add("--ansi", "--no-sort") == Options().ansi.no_sort

    assert str(Options().ansi.no_sort) == "--ansi --no-sort"


def test_options_type():
    def assert_type_equality(x, t):
        assert isinstance(x, t), f"{type(x)}: {x}"

    assert_type_equality(Options().ansi, Options)
    assert_type_equality(Options().ansi + Options().multiselect, Options)


def test_options_working():
    unknown_options = []
    for option in get_args(FzfOption):
        try:
            subprocess.run(["fzf", "--version", option], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as err:
            if "unknown option" in err.stderr:
                unknown_options.append(option)

    if unknown_options:
        raise ValueError(f"Options {unknown_options} are not recognized by fzf")


if __name__ == "__main__":
    test_options_working()
