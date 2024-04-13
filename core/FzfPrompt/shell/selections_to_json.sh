#!/usr/bin/env bash

for sel in "$@"; do echo "$sel"; done | jq -Rs --compact-output 'split("\n") | map(select(. !=""))'
