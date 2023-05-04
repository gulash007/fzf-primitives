# black magic layer
from dataclasses import dataclass, field
from datetime import datetime

from ..FzfPrompt.options import Options, Position
from ..FzfPrompt.Server import ServerCall
from .ActionMenu import Action, ActionMenu
from .Previewer import Preview, Previewer


# TODO: socket solution
@dataclass
class PromptData:
    """Accessed through socket Server"""

    id: str = field(init=False, default_factory=lambda: datetime.now().isoformat())
    choices: list = field(default_factory=list)
    previewer: Previewer = field(default_factory=Previewer)
    action_menu: ActionMenu = field(default_factory=ActionMenu)
    server_calls: dict[str, ServerCall] = field(default_factory=dict)
    options: Options = field(default_factory=Options)
    query: str = ""  # TODO: Preset query (--query option)
    selections: list[str] = field(init=False, default_factory=list)

    def update(self, query, selections):
        self.query = query
        self.selections = selections

    def add_action(self, action: Action):
        self.action_menu.add(action)

    def add_preview(self, preview: Preview):
        self.previewer.add_preview(preview)
        self.add_server_call(preview.server_call())

    def add_server_call(self, server_call: ServerCall):
        self.server_calls[server_call.name] = server_call

    def resolve_server_calls(self, socket_number: int):
        for server_call in self.server_calls.values():
            self.action_menu.add(server_call.action(socket_number))

    def resolve_options(self) -> Options:
        return self.options + self.previewer.resolve_options() + self.action_menu.resolve_options()


# TODO: Ability to output preview in Result (or anything else)
# TODO: id should be replaced in fzf options with commands in them that work with stored PromptData

# TODO: how to get current preview command so that updating data also updates current preview output?
# TODO: caching?
# TODO: preview should try to read from prompt data instead of calculating the output again
# TODO: store all line identities for easy transformations of lines?
