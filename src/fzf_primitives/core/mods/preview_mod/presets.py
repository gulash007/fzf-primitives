import json

from ...FzfPrompt import PromptData


def preview_basic(prompt_data: PromptData):
    return json.dumps(
        {
            "query": prompt_data.query,
            "current_index": prompt_data.current_index,
            "current": prompt_data.current,
            "selected_indices": prompt_data.selected_indices,
            "selections": prompt_data.selections,
            "target_indices": prompt_data.target_indices,
            "targets": prompt_data.targets,
        },
        indent=4,
        default=str,
    )


def get_fzf_json(prompt_data: PromptData, FZF_PORT: str):
    import json

    import requests

    return json.dumps(requests.get(f"http://127.0.0.1:{FZF_PORT}").json(), indent=2)


def get_fzf_env_vars(
    prompt_data: PromptData,
    FZF_LINES,
    FZF_COLUMNS,
    FZF_TOTAL_COUNT,
    FZF_MATCH_COUNT,
    FZF_SELECT_COUNT,
    FZF_POS,
    FZF_QUERY,
    FZF_INPUT_STATE,
    FZF_NTH,
    FZF_PROMPT,
    FZF_GHOST,
    FZF_POINTER,
    FZF_PREVIEW_LABEL,
    FZF_BORDER_LABEL,
    FZF_LIST_LABEL,
    FZF_INPUT_LABEL,
    FZF_HEADER_LABEL,
    FZF_ACTION,
    FZF_KEY,
    FZF_PORT,
    FZF_PREVIEW_TOP,
    FZF_PREVIEW_LEFT,
    FZF_PREVIEW_LINES,
    FZF_PREVIEW_COLUMNS,
):
    local_variables = locals().copy()
    local_variables.pop("prompt_data", None)
    return json.dumps(local_variables, indent=4, ensure_ascii=False, sort_keys=True)
