#!/usr/bin/env python3


import json
import socket
import sys
from typing import TypedDict


class PromptState(TypedDict):
    query: str
    single_index: int | None
    single_line: str | None
    indices: list[int]
    lines: list[str]


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
    prompt_state: PromptState = {
        "query": sys.argv[3],
        "single_index": int(x) if (x := sys.argv[4]) else None,
        "single_line": sys.argv[5] or None,
        "indices": list(map(int, sys.argv[6].split())),
        "lines": sys.argv[7].splitlines(),
    }
    kwargs = dict(zip(sys.argv[8::2], sys.argv[9::2]))
    return port, endpoint_id, prompt_state, kwargs


if __name__ == "__main__":
    port, endpoint_id, prompt_state, kwargs = parse_args()
    if response := make_server_call(port, endpoint_id, prompt_state, **kwargs):
        print(response)
