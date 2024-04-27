from pathlib import Path

SHELL_SCRIPT_DIR = Path(__file__).parent


class SHELL_SCRIPTS:
    make_server_call = SHELL_SCRIPT_DIR.joinpath("make_server_call.py").absolute()
    indices_to_json = SHELL_SCRIPT_DIR.joinpath("indices_to_json.sh").absolute()
    selection_to_json = SHELL_SCRIPT_DIR.joinpath("selection_to_json.sh").absolute()
    selections_to_json = SHELL_SCRIPT_DIR.joinpath("selections_to_json.sh").absolute()
