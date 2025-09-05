#!/usr/bin/env python3


import json
import socket
import sys
from typing import TypedDict


class PromptState(TypedDict):
    query: str
    current_index: int | None
    selected_indices: list[int]
    target_indices: list[int]


def make_server_call(port: int, endpoint_id: str, prompt_state: PromptState | None, /, **kwargs):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("localhost", port))
        try:
            data = {"endpoint_id": endpoint_id, "prompt_state": prompt_state, "kwargs": kwargs}

            # TODO: send it through a socket to Server instead of using nc
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
    fzf_pos = int(sys.argv[4])  # FZF_POS fzf env var
    fzf_select_count = int(sys.argv[5])  # FZF_SELECT_COUNT fzf env var
    nplus_placeholder_indices = [int(x) for x in sys.argv[6].split() if x.isdigit()]  # {+n} fzf placeholder
    selected_indices = nplus_placeholder_indices if fzf_select_count > 0 else []
    prompt_state: PromptState = {
        "query": query,
        "current_index": fzf_pos - 1 if fzf_pos > 0 else None,
        "selected_indices": selected_indices,
        "target_indices": nplus_placeholder_indices,  # selected indices or current index if nothing selected
    }
    kwargs = dict(zip(sys.argv[7::2], sys.argv[8::2]))
    return port, endpoint_id, prompt_state, kwargs


if __name__ == "__main__":
    port, endpoint_id, prompt_state, kwargs = parse_args()
    if response := make_server_call(port, endpoint_id, prompt_state, **kwargs):
        print(response)
