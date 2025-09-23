import json
import re
from pathlib import Path


def get_fzf_options():
    """❗ Requires manual clean up"""
    path_to_man_fzf = Path(__file__).parent / "options.go"
    # get all --options from file
    text = path_to_man_fzf.read_text("utf-8")
    options = re.findall(r'(--[a-zA-Z0-9\-]+)(?:[ "=\[]|,|\n)', text)
    return sorted(set(options))


def get_grouped_fzf_options():
    import subprocess

    fzf_options = get_fzf_options()
    have_negative_version = []
    do_not_have_negative_version = []
    lone_negative_options = []
    unused_options = []
    unrecognized_options = []
    erroneous_options = []
    for option in fzf_options:
        if option in UNUSED_OPTIONS:
            unused_options.append(option)
            continue
        elif option.startswith("--no-"):
            if (positive_option := option.replace("--no-", "--")) not in fzf_options:
                lone_negative_options.append(option)
            elif positive_option in UNUSED_OPTIONS:
                unused_options.append(option)
            continue
        try:
            subprocess.run(
                ["fzf", "--version", option.replace("--", "--no-")], check=True, capture_output=True, text=True
            )
            have_negative_version.append(option)
        except subprocess.CalledProcessError as err:
            if "unknown option" in err.stderr:
                do_not_have_negative_version.append(option)
            else:
                erroneous_options.append(option)
    for option in lone_negative_options.copy():
        positive_option = option.replace("--no-", "--")
        try:
            subprocess.run(["fzf", "--version", positive_option], check=True, capture_output=True, text=True)
            have_negative_version.append(positive_option)
            lone_negative_options.remove(option)
        except subprocess.CalledProcessError as err:
            if "unknown option" in err.stderr:
                continue
            else:
                erroneous_options.append(positive_option)

    return {
        "have_negative_version": sorted(have_negative_version),
        "do_not_have_negative_version": sorted(do_not_have_negative_version),
        "lone_negative_options": sorted(lone_negative_options),
        "unused_options": sorted(unused_options),
        "unrecognized_options": sorted(unrecognized_options),
        "erroneous_options": sorted(erroneous_options),
    }


UNUSED_OPTIONS = [
    "--bash",
    "--fish",
    "--zsh",
    "--man",
    "--help",
    "--version",
    "--no-winpty",
    "--toggle-sort",
    "--proxy-script",
    "--profile-block",
    "--profile-cpu",
    "--profile-mem",
    "--profile-mutex",
    "--extended-exact",
    "--async",
    "--phony",
    "--inline-info",
    "--force-tty-in",
]

if __name__ == "__main__":
    # print(get_fzf_options())
    # print(get_grouped_fzf_options())

    with open(Path(__file__).parent / "fzf_options_grouped.json", "w", encoding="utf-8") as f:
        json.dump(
            get_grouped_fzf_options(),
            f,
            indent=2,
        )
        f.write("\n")

    # assumes fzf_options_grouped.json is cleaned up
    with open(Path(__file__).parent / "fzf_options_grouped.json", "r", encoding="utf-8") as f:
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
