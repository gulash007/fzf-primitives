from fzf_primitives import Prompt

ENTRIES = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "Los Angeles"},
    {"name": "Charlie", "age": 35, "city": "Chicago"},
]


def test_current():
    prompt = Prompt(ENTRIES, lambda x: x["name"])
    prompt.mod.options.initial_query("ar")  # matches Charlie
    prompt.mod.automate("enter")
    result = prompt.run()
    assert result.current_index == 2, f"Expected index 2, got {result.current_index}"
    assert result.current == ENTRIES[2], f"Expected {ENTRIES[2]}, got {result.current}"


def test_selections():
    prompt = Prompt(ENTRIES, lambda x: x["name"])
    prompt.mod.options.multiselect.initial_query("a")  # matches Alice and Charlie
    prompt.mod.automate_actions("select-all")
    prompt.mod.automate(prompt.config.default_accept_hotkey)

    result = prompt.run()

    expected_selections = [ENTRIES[0], ENTRIES[2]]
    assert result.selections == expected_selections, f"Expected {expected_selections}, got {result.selections}"


def test_targets():
    prompt = Prompt(ENTRIES, lambda x: x["name"])
    prompt.mod.options.multiselect.initial_query("o")  # matches Bob
    prompt.mod.automate(prompt.config.default_accept_hotkey)
    result = prompt.run()

    expected_targets = [ENTRIES[1]]
    targets = list(result)
    assert targets == expected_targets, f"Expected {expected_targets}, got {targets}"

    prompt = Prompt(ENTRIES, lambda x: x["name"])
    prompt.mod.options.multiselect.initial_query("a")  # matches Alice and Charlie
    prompt.mod.automate_actions("select-all")
    prompt.mod.automate(prompt.config.default_accept_hotkey)
    result = prompt.run()

    expected_targets = [ENTRIES[0], ENTRIES[2]]
    targets = list(result)
    assert targets == expected_targets, f"Expected {expected_targets}, got {targets}"


if __name__ == "__main__":
    test_current()
