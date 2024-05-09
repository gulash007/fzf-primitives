from ..actions import ShellCommand
from ..core.FzfPrompt.action_menu.binding import Binding
import pytest


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


def get_binding_cycling():
    binding1 = Binding("Some binding", ShellCommand("echo -n first && read"))
    binding2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
    binding3 = Binding("Some third binding", ShellCommand("echo -n third && read"))

    return (binding1 | binding2) | binding3


def test_binding_addition_associative():
    binding1 = Binding("Some binding", ShellCommand("echo -n first && read"))
    binding2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
    binding3 = Binding("Some third binding", ShellCommand("echo -n third && read"))

    binding12_3 = (binding1 + binding2) + binding3
    binding1_23 = binding1 + (binding2 + binding3)

    assert binding12_3.name == binding1_23.name
    assert binding12_3.description == binding1_23.description
    assert [action for ag in binding12_3._action_groups.values() for action in ag.actions] == [
        action for ag in binding1_23._action_groups.values() for action in ag.actions
    ]


def test_binding_cycling_closed_in_cycling():
    binding1 = Binding("Some binding", ShellCommand("echo -n first && read"))
    binding2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
    binding3 = Binding("Some third binding", ShellCommand("echo -n third && read"))
    binding4 = Binding("Some fourth binding", ShellCommand("echo -n fourth && read"))

    binding12 = binding1 | binding2
    binding34 = binding3 | binding4
    binding1234 = binding12 | binding34

    assert binding1234.name == (ex := (binding1 | binding2 | binding3 | binding4)).name
    assert binding1234.description == ex.description
    assert [action for ag in binding1234._action_groups.values() for action in ag.actions] == [
        action for ag in ex._action_groups.values() for action in ag.actions
    ]

    # not closed in addition though
    with pytest.raises(NotImplementedError):
        binding12 + binding34


def test_binding_cycling_associative():
    binding1 = Binding("Some binding", ShellCommand("echo -n first && read"))
    binding2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
    binding3 = Binding("Some third binding", ShellCommand("echo -n third && read"))

    binding12or3 = (binding1 | binding2) | binding3
    binding1or23 = binding1 | (binding2 | binding3)

    assert binding12or3.name == binding1or23.name
    assert binding12or3.description == binding1or23.description
    assert [action for ag in binding12or3._action_groups.values() for action in ag.actions] == [
        action for ag in binding1or23._action_groups.values() for action in ag.actions
    ]


def test_addition_distributive_over_cycling():
    """a + (b | c) == (a + b) | (a + c)"""
    binding1 = Binding("Some binding", ShellCommand("echo -n first && read"))
    binding2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
    binding3 = Binding("Some third binding", ShellCommand("echo -n third && read"))

    # distributive from left
    binding_1_2or3 = binding1 + (binding2 | binding3)
    binding_1_2or1_3 = (binding1 + binding2) | (binding1 + binding3)

    assert binding_1_2or3.name == binding_1_2or1_3.name
    assert binding_1_2or3.description == binding_1_2or1_3.description
    assert [action for ag in binding_1_2or3._action_groups.values() for action in ag.actions] == [
        action for ag in binding_1_2or1_3._action_groups.values() for action in ag.actions
    ]

    # distributive from right
    binding_1or2_3 = (binding1 | binding2) + binding3
    binding_1_3or2_3 = (binding1 + binding3) | (binding2 + binding3)

    assert binding_1or2_3.name == binding_1_3or2_3.name
    assert binding_1or2_3.description == binding_1_3or2_3.description
    assert [action for ag in binding_1or2_3._action_groups.values() for action in ag.actions] == [
        action for ag in binding_1_3or2_3._action_groups.values() for action in ag.actions
    ]


def test_binding_addition_closed():
    """if a . b is ok, then (a + c) . (b + c) is also ok (. can be + or |)"""
    binding1 = Binding("Some binding", ShellCommand("echo -n first && read"))
    binding2 = Binding("Some other binding", ShellCommand("echo -n second && read"))
    binding3 = Binding("Some third binding", ShellCommand("echo -n third && read"))
    binding4 = Binding("Some fourth binding", ShellCommand("echo -n fourth && read"))

    binding1or2 = binding1 | binding2
    binding1or2_3 = binding1or2 + binding3
    binding1or2_3 | binding4


if __name__ == "__main__":
    print(get_binding_cycling())
