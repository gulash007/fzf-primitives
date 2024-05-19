#!/usr/bin/env python3


import json
import socket
import sys
from itertools import zip_longest


def grouper(iterable, n, *, incomplete="fill", fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == "strict":
        return zip(*args, strict=True)
    if incomplete == "ignore":
        return zip(*args)
    else:
        raise ValueError("Expected fill, strict, or ignore")


if __name__ == "__main__":
    port = int(sys.argv[1])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("localhost", port))
        try:
            server_call_id, command_type, query, single_index, single_line, indices, selections = sys.argv[2:9]
            data = {
                "server_call_id": server_call_id,
                "command_type": command_type,
                "prompt_state": {
                    "query": query,
                    "single_index": int(single_index) if single_index else None,
                    "single_line": single_line or None,
                    "indices": list(map(int, indices.split())),
                    "lines": selections.splitlines(),
                },
                "kwargs": {},
            }
            for key, value in grouper(sys.argv[9:], 2, incomplete="strict"):
                data["kwargs"][key] = value

            # TODO: send it through a socket to Server instead of using nc
            payload = json.dumps(data).encode("utf-8")
        except Exception as err:
            payload = f"{sys.argv}\n{err}".encode("utf-8")

        client.send(len(payload).to_bytes(4))
        client.sendall(payload)

        response_length = int.from_bytes(client.recv(4))
        if response := client.recv(response_length, socket.MSG_WAITALL).decode("utf-8"):
            print(response)
