from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from ..options import Trigger
    from ..prompt_data import PromptData
    from .actions import ServerCallFunction


class ServerEndpoint:
    def __init__(self, function: ServerCallFunction, id: str, trigger: Trigger) -> None:
        self.function = function
        self.id = id
        self.trigger: Trigger = trigger

    def run(self, prompt_data: PromptData, request: Request) -> Any:
        if request.prompt_state:
            prompt_data.set_state(request.prompt_state, self.trigger)
        return self.function(prompt_data, **request.kwargs)


class Request:
    def __init__(self, endpoint_id: str, prompt_state: PromptState | None, kwargs: dict):
        self.endpoint_id = endpoint_id
        self.prompt_state = prompt_state
        self.kwargs = kwargs

    @classmethod
    def from_json(cls, data: dict) -> Self:
        prompt_state = PromptState.from_json(data["prompt_state"]) if data["prompt_state"] else None
        return cls(data["endpoint_id"], prompt_state, data["kwargs"])


class PromptState:
    def __init__(
        self,
        query: str,
        current_index: int | None,
        selected_count: int,
        target_indices: list[int],  # expanded {+n} fzf placeholder
    ):
        self.query = query
        self.current_index = current_index
        self.selected_count = selected_count
        self.target_indices = target_indices

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**data)

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)
