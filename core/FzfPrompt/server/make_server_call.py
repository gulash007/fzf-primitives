#!/usr/bin/env python3


import json
import sys
from itertools import zip_longest
from multiprocessing.connection import Client


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
    port = sys.argv[1]
    address = ("localhost", int(port))
    with Client(address, authkey=b"secret password") as client:
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

            payload = json.dumps(data)
        except Exception as e:
            payload = f"{sys.argv[1:]}\n{e}"
        client.send(payload)
        if response := client.recv():
            print(response)
        client.close()
