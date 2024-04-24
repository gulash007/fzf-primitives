#!/usr/bin/env bash

# Increment "current_index" and select the corresponding element, and update the file
# Example JSON file format: {"current_index":2,"all":["one","two","three"],"length":3}
incremented_data=$(jq '.current_index = (.current_index + 1) % .length' "$1" --compact-output) &&
    jq '.all[.current_index]' -r <<<"$incremented_data" &&
    echo "$incremented_data" >"$1"
