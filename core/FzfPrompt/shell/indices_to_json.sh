#!/usr/bin/env bash

jq --null-input --compact-output '[$ARGS.positional[] | tonumber]' --args "$@"
