from ..core.FzfPrompt.options import Options


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
