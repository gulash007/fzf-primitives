def construct_command(file_name: str, indices: bool = False):
    command = f"python3.11 -m fzf_primitives.core.actions.{file_name}"
    arguments = ["--", "{q}", "{+}"]  # -- allows for query and selections containing leading hyphens
    if indices:
        arguments.insert(0, "--with-indices")
        arguments.append("{+n}")
    return f"execute({command} {' '.join(arguments)})"


class ACTION:
    open = "execute(open {+})"
    obsidian_open_files = construct_command("obsidian_open_files")
    view_file = construct_command("view_file")
    # clip_preview = "" # TODO: Needs to read from prompt data
