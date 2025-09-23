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
    assert Options().ansi.no_sort != Options().no_sort.ansi


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


# HEADER/FOOTER
def test_adding_headers_and_footers():
    opts = Options().add_header("Header 1").add_header("Header 2").add_footer("Footer 1").add_footer("Footer 2")
    assert "--header=Header 1\nHeader 2" in opts
    assert "--footer=Footer 1\nFooter 2" in opts


def test_extend_header_appends_with_custom_separator():
    opts = Options("--header=Initial Header")
    opts.add_header("Extra Header", separator=" | ")
    assert any(opt == "--header=Initial Header | Extra Header" for opt in opts.options)


def test_extend_header_adds_header_if_not_present():
    opts = Options("--layout=reverse")
    opts.add_header("New Header")
    assert any(opt == "--header=New Header" for opt in opts.options)


def test_extend_header_multiple_headers_only_last_extended():
    opts = Options("--header=First", "--header=Second")
    opts.add_header("Extra")
    # Only the last header should be extended
    assert opts.options[-1] == "--header=Second\nExtra"
    assert opts.options[-2] == "--header=First"


if __name__ == "__main__":
    test_options_working()
