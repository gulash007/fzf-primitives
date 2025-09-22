import json
import re
from pathlib import Path


def get_fzf_options():
    """❗ Requires manual clean up"""
    path_to_man_fzf = Path(__file__).parent / "man_fzf.txt"
    # get all --options from file
    text = (
        path_to_man_fzf.read_text("utf-8")
        .replace("file --brief", "")
        .replace("git log --oneline --graph", "")
        .replace("git log --oneline", "")
        .replace("git grep --line-number", "")
        .replace("rg --column --line-number --no-heading --color=always --smart-case", "")
        .replace("--no- prefix", "")
        .replace("setting --tty-", "")
    )
    options = re.findall(r"(--[a-zA-Z0-9\-]+)(?:[ =\[]|,|\n)", text)
    return sorted(set(options))


def get_sorted_by_negative_options():
    import subprocess

    fzf_options = get_fzf_options()
    have_negative_version = []
    do_not_have_negative_version = []
    lone_negative_options = []
    unused_options = []
    for option in fzf_options:
        if option in UNUSED_OPTIONS:
            unused_options.append(option)
            continue
        elif option.startswith("--no-"):
            if option.replace("--no-", "--") not in fzf_options:
                lone_negative_options.append(option)
            continue
        try:
            subprocess.run(["fzf", option.replace("--", "--no-"), "--version"], check=True, capture_output=True)
            have_negative_version.append(option)
        except subprocess.CalledProcessError:
            do_not_have_negative_version.append(option)

    return {
        "have_negative_version": sorted(have_negative_version),
        "do_not_have_negative_version": sorted(do_not_have_negative_version),
        "lone_negative_options": sorted(lone_negative_options),
        "unused_options": sorted(unused_options),
    }


UNUSED_OPTIONS = ["--bash", "--fish", "--zsh", "--man", "--help", "--version"]

if __name__ == "__main__":
    # print(get_fzf_options())
    # print(get_sorted_by_negative_options())

    with open(Path(__file__).parent / "fzf_options_by_negative.json", "w", encoding="utf-8") as f:
        json.dump(
            get_sorted_by_negative_options(),
            f,
            indent=2,
        )
        f.write("\n")

    # assumes fzf_options_by_negative.json is cleaned up
    with open(Path(__file__).parent / "fzf_options_by_negative.json", "r", encoding="utf-8") as f:
        obj = json.load(f)
    with open(Path(__file__).parent / "fzf_options.json", "w", encoding="utf-8") as f:
        json.dump(
            sorted(
                [
                    *obj["have_negative_version"],
                    *[f"--no-{opt[2:]}" for opt in obj["have_negative_version"]],
                    *obj["do_not_have_negative_version"],
                    *obj["lone_negative_options"],
                ]
            ),
            f,
            indent=2,
        )
        f.write("\n")
