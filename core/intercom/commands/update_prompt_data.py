from ..commands.functions import load_json_file, dump_to_json_file
from ..PromptData import PromptData
import sys


def main(prompt_id: str, query: str, *selections: str):
    path = PromptData.get_path_from_id(prompt_id)
    obj = load_json_file(path)
    obj["query"] = query
    obj["selections"] = selections
    dump_to_json_file(obj, path)


if __name__ == "__main__":
    main(*sys.argv[1:])
