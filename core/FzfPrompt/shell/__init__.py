from pathlib import Path

SHELL_SCRIPT_DIR = Path(__file__).parent


class SHELL_SCRIPTS:
    make_server_call = SHELL_SCRIPT_DIR.joinpath("make_server_call.py").absolute()
