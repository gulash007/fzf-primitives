#!/usr/bin/env bash

this_script_path="$(realpath "$0")"
this_script_dir="$(dirname "$this_script_path")"
test_output_file="$this_script_dir/test_output.ansi"

source "$this_script_dir/setup.sh"

json_data_path="$this_script_dir/fzf_data.json"

fzf --preview 'echo {}' --bind "enter:transform(\"$this_script_dir/get-cyclical-next-value.sh\" \"$json_data_path\")"
