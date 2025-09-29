import pytest

from fzf_primitives.actions import ShellCommand
from fzf_primitives.core.FzfPrompt.action_menu.binding import Binding

BINDING1 = Binding("Some binding", ShellCommand("echo -n first && read"))
BINDING2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
BINDING3 = Binding("Some third binding", ShellCommand("echo -n third && read"))
BINDING4 = Binding("Some fourth binding", ShellCommand("echo -n fourth && read"))


@pytest.mark.parametrize(
    ["self", "other", "expected_name"],
    [
        (Binding(None, "select-all"), Binding(None, "clear-selection"), "select-all -> clear-selection"),
        (Binding("Run command", ShellCommand("echo")), Binding(None, "select-all"), "Run command -> select-all"),
    ],
)
def test_names_after_binding_addition(self: Binding, other: Binding, expected_name: str):
    result = self + other
    assert result.name == expected_name


# ruff: noqa: SLF001


def test_binding_addition_associative():
    binding12_3 = (BINDING1 + BINDING2) + BINDING3
    binding1_23 = BINDING1 + (BINDING2 + BINDING3)

    assert binding12_3.name == binding1_23.name
    assert binding12_3.description == binding1_23.description
    assert [action for ag in binding12_3._action_groups.values() for action in ag.actions] == [
        action for ag in binding1_23._action_groups.values() for action in ag.actions
    ]


def test_binding_cycling_closed_in_cycling():
    binding12 = BINDING1 | BINDING2
    binding34 = BINDING3 | BINDING4
    binding1234 = binding12 | binding34

    assert binding1234.name == (ex := (BINDING1 | BINDING2 | BINDING3 | BINDING4)).name
    assert binding1234.description == ex.description
    assert [action for ag in binding1234._action_groups.values() for action in ag.actions] == [
        action for ag in ex._action_groups.values() for action in ag.actions
    ]

    # not closed in addition though
    with pytest.raises(NotImplementedError):
        binding12 + binding34


def test_binding_cycling_associative():
    binding12or3 = (BINDING1 | BINDING2) | BINDING3
    binding1or23 = BINDING1 | (BINDING2 | BINDING3)

    assert binding12or3.name == binding1or23.name
    assert binding12or3.description == binding1or23.description
    assert [action for ag in binding12or3._action_groups.values() for action in ag.actions] == [
        action for ag in binding1or23._action_groups.values() for action in ag.actions
    ]


def test_addition_distributive_over_cycling():
    """a + (b | c) == (a + b) | (a + c)"""

    # distributive from left
    binding_1_2or3 = BINDING1 + (BINDING2 | BINDING3)
    binding_1_2or1_3 = (BINDING1 + BINDING2) | (BINDING1 + BINDING3)

    assert binding_1_2or3.name == binding_1_2or1_3.name
    assert binding_1_2or3.description == binding_1_2or1_3.description
    assert [action for ag in binding_1_2or3._action_groups.values() for action in ag.actions] == [
        action for ag in binding_1_2or1_3._action_groups.values() for action in ag.actions
    ]

    # distributive from right
    binding_1or2_3 = (BINDING1 | BINDING2) + BINDING3
    binding_1_3or2_3 = (BINDING1 + BINDING3) | (BINDING2 + BINDING3)

    assert binding_1or2_3.name == binding_1_3or2_3.name
    assert binding_1or2_3.description == binding_1_3or2_3.description
    assert [action for ag in binding_1or2_3._action_groups.values() for action in ag.actions] == [
        action for ag in binding_1_3or2_3._action_groups.values() for action in ag.actions
    ]


def test_binding_addition_closed():
    """if a . b is ok, then (a + c) . (b + c) is also ok (. can be + or |)"""

    binding1or2 = BINDING1 | BINDING2
    binding1or2_3 = binding1or2 + BINDING3
    binding1or2_3 | BINDING4


def test_addition_precedence_over_cycling():
    binding1_2or3_4 = BINDING1 + BINDING2 | BINDING3 + BINDING4
    binding12or34 = (BINDING1 + BINDING2) | (BINDING3 + BINDING4)

    assert binding1_2or3_4.name == binding12or34.name
    assert binding1_2or3_4.description == binding12or34.description
    assert [action for ag in binding1_2or3_4._action_groups.values() for action in ag.actions] == [
        action for ag in binding12or34._action_groups.values() for action in ag.actions
    ]


def get_binding_cycling():
    return (BINDING1 | BINDING2) | BINDING3


if __name__ == "__main__":
    print(get_binding_cycling())
