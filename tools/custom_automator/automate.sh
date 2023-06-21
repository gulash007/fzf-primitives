#!/usr/bin/env bash

while read -r line; do
    curl -XPOST "localhost:$1" -d "$line"; sleep 0.25
done <"/Users/honza/Documents/Projects/PythonPackages/fzf_primitives/experimental/core/FzfPrompt/to_automate.txt"
