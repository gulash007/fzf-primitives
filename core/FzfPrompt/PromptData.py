# black magic layer
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from ..FzfPrompt.options import Hotkey, Options, Position
from .ActionMenu import Action, ActionMenu
from .Previewer import Preview, Previewer


@dataclass
class PromptData:
    """Accessed through socket Server"""

    id: str = field(init=False, default_factory=lambda: datetime.now().isoformat())
    choices: list = field(default_factory=list)
    previewer: Previewer = field(default_factory=Previewer)
    action_menu: ActionMenu = field(default_factory=ActionMenu)
    options: Options = field(default_factory=Options)

    # def update(self, query, selections):
    #     self.query = query
    #     self.selections = selections

    def get_current_preview(self) -> str:
        return self.previewer.current_preview.output

    def add_preview(self, preview: Preview):
        self.previewer.add(preview, self.action_menu)

    def resolve_options(self) -> Options:
        return self.options + self.previewer.resolve_options() + self.action_menu.resolve_options()


# TODO: Ability to output preview in Result (or anything else)
# TODO: id should be replaced in fzf options with commands in them that work with stored PromptData

# TODO: how to get current preview command so that updating data also updates current preview output?
# TODO: caching?
# TODO: preview should try to read from prompt data instead of calculating the output again
# TODO: store all line identities for easy transformations of lines?
