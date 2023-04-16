import json
from ..PromptData import PromptData


def load_json_file(path):
    with open(path, "r", encoding="utf8") as json_file:
        return json.load(json_file)


def get_preview(prompt_id: str, preview_id: str) -> str:
    prompt_data = PromptData.load(prompt_id)
    return prompt_data.get_preview_output(preview_id)
