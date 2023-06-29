#!/usr/bin/env bash

while read -r line; do
    curl -XPOST "localhost:$1" -d "$line"
    sleep 0.25
done <"$(dirname "$0")/to_automate.txt"
