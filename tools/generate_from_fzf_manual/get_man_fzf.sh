#!/usr/bin/env bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_file="$script_dir/man_fzf.txt"

echo "Generating fzf manual for version $(fzf --version) into $output_file"
MANWIDTH=140 man fzf | col -b > "$output_file"
