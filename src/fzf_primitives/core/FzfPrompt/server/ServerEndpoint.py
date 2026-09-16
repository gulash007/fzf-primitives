from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..options import Trigger
    from ..prompt_data import PromptData
    from .actions import ServerCallFunction


class ServerEndpoint:
    def __init__(self, function: ServerCallFunction, id: str, trigger: Trigger, bg: bool = False) -> None:
        self.function = function
        self.id = id
        self.trigger: Trigger = trigger
        self.bg: bool = bg

    def run(self, prompt_data: PromptData, fields: list[str]) -> Any:
        query = fields[0]
        current_index = int(fields[1]) if fields[1].isdigit() else None
        selected_count = int(fields[2])
        target_indices = [int(x) for x in fields[3].split() if x.isdigit()]
        prompt_data.set_state(PromptState(query, current_index, selected_count, target_indices), self.trigger)
        kwargs = {k: v for k, v in zip(fields[4::2], fields[5::2])}
        return self.function(prompt_data, **kwargs)


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

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)
