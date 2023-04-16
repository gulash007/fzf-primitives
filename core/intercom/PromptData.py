from typing import Self, Protocol
from pydantic import BaseModel, parse_raw_as

from ..actions.preview_basic import preview_basic

from ..options import Options
from .constants import STORAGE_PATH
from pathlib import Path
from dataclasses import dataclass


class PreviewFunction(Protocol):
    @staticmethod
    def __call__(query: str, selections: list[tuple[int, str]]) -> str:
        ...


FUNCTIONS = {"basic": preview_basic}


class Preview(BaseModel):
    id: str
    output: str | None = None
    # function: PreviewFunction | None = None
    # command: str | None = None

    def run_function(self, query, selections):
        return FUNCTIONS[self.id](query, selections)

    def update(self, query, selections):
        self.output = FUNCTIONS[self.id](query, selections)


# TODO: socket solution
class PromptData(BaseModel):
    """A prompt should be reproducible with this data. Basically any program (and therefore fzf) should
    be able to deserialize it and access it"""

    id: str
    previews: dict[str, Preview]
    choices: list[str]
    # options: Options  # TODO: how to serialize and deserialize
    query: str = ""  # TODO: Preset query (--query option)
    selections: list[str] = []  # TODO: preset selections?

    @classmethod
    def load(cls, prompt_id: str) -> Self:
        return parse_raw_as(cls, cls.read(prompt_id))

    @classmethod
    def read(cls, prompt_id: str):
        with open(cls.get_path_from_id(prompt_id), "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def get_path_from_id(cls, prompt_id: str) -> Path:
        return STORAGE_PATH.joinpath(f"{prompt_id}.json")

    def save(self):
        with open(self.get_path_from_id(self.id), "w", encoding="utf-8") as f:
            f.write(self.json())

    # TODO: bound change and focus actions need to be executed before running --preview command
    def update(self, query, selections, preview_id):
        self.query = query
        self.selections = selections
        self.previews[preview_id].update(query, selections)
        self.save()

    def get_preview_output(self, preview_id: str) -> str:
        preview = self.previews[preview_id]
        return preview.output or preview.run_function(self.query, self.selections)


# TODO: Ability to output preview in Result (or anything else)
# TODO: id should be replaced in fzf options with commands in them that work with stored PromptData

# TODO: On event 'change' and 'focus' the prompt data file should be updated
# TODO: how to get current preview command so that updating data also updates current preview output?
# TODO: caching?
# TODO: preview should try to read from prompt data instead of calculating the output again
# TODO: store all line identities for easy transformations of lines?
