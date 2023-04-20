import json
from ..PromptData import PromptData


def load_json_file(path):
    with open(path, "r", encoding="utf8") as json_file:
        return json.load(json_file)


def dump_to_json_file(data, path):
    with open(path, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, default=lambda x: x.__dict__, indent=2, ensure_ascii=False)


def get_preview(preview_id: str) -> str:
    prompt_data = PromptData.load(prompt_id)
    return prompt_data.get_preview_output(preview_id)
