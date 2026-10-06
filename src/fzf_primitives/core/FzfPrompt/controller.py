from __future__ import annotations

from typing import TypedDict

from ..monitoring import LoggedComponent
from .action_menu import Binding


class Controller(LoggedComponent):
    """Can control any prompt that uses --listen option including the one it's attached to"""

    def execute(self, port: int, binding: Binding):
        """Executes a binding"""
        from urllib.request import Request, urlopen

        try:
            req = Request(
                f"http://localhost:{port}",
                data=binding.action_string().encode(),
                method="POST",
            )
            with urlopen(req) as response:
                message = response.read().decode()
            if message:
                if not message.startswith("unknown action:"):
                    self.logger.log("WEIRDNESS", message, trace_point="weirdness_executing_binding")
                raise RuntimeError(message)
        except Exception as e:
            self.logger.exception(str(e), trace_point="error_executing_binding")

    def get_state_json(self, port: int) -> ExperimentalStateJson:
        """Gets the state of the prompt as a dictionary"""
        import json
        from urllib.error import HTTPError
        from urllib.request import urlopen

        try:
            with urlopen(f"http://localhost:{port}") as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to get state: {response.read().decode()}")
                return json.loads(response.read().decode())
        except HTTPError as e:
            raise RuntimeError(f"Failed to get state: {e.read().decode()}") from e


class ExperimentalStateJson(TypedDict):
    reading: bool
    progress: int
    query: str
    position: int
    sort: bool
    totalCount: int
    matchCount: int
    current: Line
    matches: list[Line]
    selected: list[Line]


class Line(TypedDict):
    index: int
    text: str
