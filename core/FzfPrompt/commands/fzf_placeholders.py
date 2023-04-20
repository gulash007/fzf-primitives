class PLACEHOLDERS:
    query = "{q}"
    selection = "{}"
    selections = "{+}"
    selections_json = "$(jq --compact-output --null-input '$ARGS.positional' --args -- {+})"
    index = "{n}"
    indices = "{+n}"
    indices_json = "$(jq --compact-output --null-input '$ARGS.positional' --args -- {+n})"
