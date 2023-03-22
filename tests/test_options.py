from core.options import Options


def test_options():
    assert Options("--ansi") == Options("--ansi")
    assert Options("--ansi", "--no-sort") == Options("--ansi", "--no-sort")
    assert Options("--ansi") >= Options("--ansi")
    assert Options("--ansi") <= Options("--ansi")
    assert Options("--ansi") != Options("--ansi", "--no-sort")
    assert Options("--ansi") < Options("--ansi", "--no-sort")
    assert Options("--ansi") <= Options("--ansi", "--no-sort")
    assert not Options("--ansi", "--multi") < Options("--ansi", "--no-sort", "--multi")
    assert Options("--ansi", "--no-sort") > Options("--ansi")
    assert not Options("--ansi", "--no-sort", "--multi") > Options("--ansi", "--multi")
    assert Options("--ansi", "--no-sort") >= Options("--ansi")
    assert not Options("--ansi", "--no-sort", "--multi") >= Options("--ansi", "--multi")

    assert Options("--ansi") + Options("--no-sort") == Options("--ansi", "--no-sort")

    assert Options("--ansi") == Options().ansi

    assert Options().add("--ansi", "--no-sort") == Options().ansi.no_sort

    assert str(Options().ansi.no_sort) == "--ansi --no-sort"
