#!/usr/bin/env bash

if [[ $* ]]; then echo -n "$*" | jq -Rs; else echo "null"; fi
