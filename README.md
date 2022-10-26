# fzf-primitives

- exit_hotkey needs to come before clip_output or else the hotkey is also clipped (which is usually undesired)
- exit_on_no_selection needs to come before exit_hotkey which would normally expect first element in output list to be the hotkey or an empty string but no selection (aborted selection) outputs empty list (or better, check for empty list in exit_hotkey)
