from ..core.mods.inspector import get_inspector_prompt
import sys


def run_remote_inspector(port: int):
    prompt = get_inspector_prompt(port)
    prompt.run()


if __name__ == "__main__":
    prompt_port = int(sys.argv[1])
    run_remote_inspector(prompt_port)
