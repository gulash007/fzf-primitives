#!/usr/bin/env bash

this_script_path="$(realpath "$0")"
this_script_dir="$(dirname "$this_script_path")"
test_output_file="$this_script_dir/test_output.ansi"

source "$this_script_dir/setup.sh"

test_find | fzf --preview 'echo {}' --bind "enter:change-preview-label(single index)+change-preview-window(up,10%)+change-preview(echo {n} && echo {n} >> $test_output_file)" --bind "esc:change-preview-label(single line)+change-preview-window(right,50%)+change-preview(echo {} && echo {} >> $test_output_file)"
