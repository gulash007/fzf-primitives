from pathlib import Path

SHELL_SCRIPT_DIR = Path(__file__).parent


class SHELL_SCRIPTS:
    indices_to_json = SHELL_SCRIPT_DIR.joinpath("indices_to_json.sh").absolute()
    selections_to_json = SHELL_SCRIPT_DIR.joinpath("selections_to_json.sh").absolute()
