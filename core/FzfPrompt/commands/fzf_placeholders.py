PLACEHOLDERS = {
    "query": "{q}",
    "selection": "{}",
    "selections": "{+}",
    "print_selections_on_new_lines": "arr=({+}) && printf '%s\\n' \"${arr[@]}\"",
    "selections_json": "$(jq --compact-output --null-input '$ARGS.positional' --args -- {+})",
    "index": "{n}",
    "indices": "{+n}",
    "indices_json": "$(jq --compact-output --null-input '$ARGS.positional' --args -- {+n})",
}
