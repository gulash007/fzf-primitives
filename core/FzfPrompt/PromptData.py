# Using black magic layer
from datetime import datetime
from pathlib import Path
from typing import Protocol, Self

from pydantic import BaseModel, Field


from ..actions.preview_basic import preview_basic
from ..FzfPrompt.options import Options


class PreviewFunction(Protocol):
    @staticmethod
    def __call__(query: str, selections: list[tuple[int, str]]) -> str:
        ...


PREVIEW_FUNCTIONS = {"no preview": lambda *args, **kwargs: None, "basic": preview_basic}


class Preview(BaseModel):
    id: str
    command: str
    output: str | None = None
    # function: PreviewFunction | None = None
    # command: str | None = None

    def run_function(self, query, selections):
        return PREVIEW_FUNCTIONS[self.id](query, selections)

    def update(self, query, selections):
        self.output = PREVIEW_FUNCTIONS[self.id](query, selections)


# TODO: socket solution
class PromptData(BaseModel):
    """Accessed through socket Server"""

    id: str = Field(const=True, default_factory=lambda: datetime.now().isoformat())
    current_preview: str = "no preview"
    choices: list = []
    previews: dict[str, Preview] = {}  # TODO: class Previewer
    options: Options = Options()  # TODO: how to serialize and deserialize
    query: str = ""  # TODO: Preset query (--query option)
    selections: list[str] = []  # TODO: preset selections?

    # TODO: bound change and focus actions need to be executed before running --preview command
    def update(self, query, selections):
        self.query = query
        self.selections = selections
        self.previews[self.current_preview].update(query, selections)

    def get_preview_output(self, preview_id: str) -> str:
        preview = self.previews[preview_id]
        return preview.output or preview.run_function(self.query, self.selections)


# TODO: Ability to output preview in Result (or anything else)
# TODO: id should be replaced in fzf options with commands in them that work with stored PromptData

# TODO: how to get current preview command so that updating data also updates current preview output?
# TODO: caching?
# TODO: preview should try to read from prompt data instead of calculating the output again
# TODO: store all line identities for easy transformations of lines?
