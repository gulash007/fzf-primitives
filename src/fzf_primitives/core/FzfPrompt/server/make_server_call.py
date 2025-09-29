#!/usr/bin/env python3


import json
import socket
import sys
from typing import TypedDict


class PromptStateDict(TypedDict):
    query: str
    current_index: int | None
    selected_count: int
    target_indices: list[int]


def make_server_call(port: int, endpoint_id: str, prompt_state: PromptStateDict, /, kwargs):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("localhost", port))
        try:
            data = {"endpoint_id": endpoint_id, "prompt_state": prompt_state, "kwargs": kwargs}
            payload = json.dumps(data).encode("utf-8")
        except Exception as err:
            payload = f"{sys.argv}\n{err}".encode("utf-8")

        client.send(len(payload).to_bytes(4))
        client.sendall(payload)

        response_length = int.from_bytes(client.recv(4))
        return client.recv(response_length, socket.MSG_WAITALL).decode("utf-8")


def parse_args():
    port = int(sys.argv[1])
    endpoint_id = sys.argv[2]
    query = sys.argv[3]  # {q} fzf placeholder
    n_placeholder = sys.argv[4]  # {n} fzf placeholder
    fzf_select_count = int(sys.argv[5])  # FZF_SELECT_COUNT fzf env var
    nplus_placeholder_indices = [int(x) for x in sys.argv[6].split() if x.isdigit()]  # {+n} fzf placeholder
    prompt_state: PromptStateDict = {
        "query": query,
        "current_index": int(n_placeholder) if n_placeholder.isdigit() else None,  # empty string if no shown entries
        "selected_count": fzf_select_count,
        "target_indices": nplus_placeholder_indices,  # selected indices or current index if nothing selected
    }
    kwargs = dict(zip(sys.argv[7::2], sys.argv[8::2]))
    return port, endpoint_id, prompt_state, kwargs


if __name__ == "__main__":
    port, endpoint_id, prompt_state, kwargs = parse_args()
    if response := make_server_call(port, endpoint_id, prompt_state, kwargs):
        sys.stdout.write(response)
