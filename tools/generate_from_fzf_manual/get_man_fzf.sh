#!/usr/bin/env bash


echo "Generating fzf manual for version $(fzf --version)..."
COLUMNS=120 man fzf | col -b > "fzf-manual.txt"
