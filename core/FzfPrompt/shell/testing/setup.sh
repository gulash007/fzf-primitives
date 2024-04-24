#!/usr/bin/env bash

this_script_path="$(realpath "$0")"
this_script_dir="$(dirname "$this_script_path")"

function test_find() { find "$this_script_dir/../../../.." -maxdepth 1 -type f -printf "%f\n"; }
