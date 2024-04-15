#!/usr/bin/env bash

if [[ $* ]]; then echo $* | jq -Rs; else echo "null"; fi
