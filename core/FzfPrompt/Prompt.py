# Black magic layer
from __future__ import annotations

import inspect
import json
import os
import re
import shlex
import socket
import subprocess
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from shutil import which
from threading import Event, Thread
from typing import Callable, Concatenate, Generic, Iterable, Literal, ParamSpec, Protocol, Self, Type, TypeVar

import clipboard
import pydantic
from thingies import shell_command

from ..monitoring.Logger import get_logger
from .decorators import single_use_method
from .exceptions import ExpectedException
from .options import FzfEvent, Hotkey, Options, ParametrizedOptionString, Position

T = TypeVar("T")

logger = get_logger()

FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Unbind some default fzf hotkeys (add bind 'hk:ignore' options from left)
# TODO: Solve other expected hotkeys
# TODO: Use tempfile
# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable specified in vscode-insiders://file/Users/honza/.dotfiles/.zshforfzf:4
def run_fzf_prompt(prompt_data: PromptData, *, executable_path=None) -> Result:
    if not which("fzf") and not executable_path:
        raise SystemError(f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")
    else:
        executable_path = "fzf"

    if (action_menu := prompt_data.action_menu).should_run_automator:
        action_menu.automator.resolve(action_menu)
        action_menu.automator.start()

    server_setup_finished = Event()
    server_should_close = Event()
    server = Server(prompt_data, server_setup_finished, server_should_close)
    server.start()
    server_setup_finished.wait()

    # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
    # TODO: 🧊 Use subprocess.run without shell=True as [executable_path, *options] (need to change Options)
    try:
        options = prompt_data.resolve_options()
        logger.debug("\n".join(options.options))
        subprocess.run(
            f"{executable_path} {options}",
            shell=True,
            input="\n".join(str(choice) for choice in prompt_data.choices).encode(),
            check=True,
            env=os.environ | {JSON_ENV_VAR_NAME: json.dumps(prompt_data.data)} if prompt_data.data_as_env_var else None,
        )
    except subprocess.CalledProcessError as err:
        if err.returncode != 130:  # 130 means aborted
            raise
    finally:
        server_should_close.set()
    server.join()
    if isinstance(e := prompt_data.result.exception, ExpectedException):
        raise e
    prompt_data.action_menu.apply_post_processor(prompt_data)
    return prompt_data.result


EndStatus = Literal["accept", "abort"]


class ResultAttr(Generic[T]):
    def __init__(self) -> None:
        self._value: T
        self._is_set = False
        self.name: str

    def __set_name__(self, obj: Result, name: str):
        self.name = name

    def __get__(self, obj: Result, objtype=None) -> T:
        if not self._is_set:
            raise RuntimeError(f"{self.name} not set")
        return self._value

    def __set__(self, obj: Result, value: T):
        self._is_set = True
        self._value = value


class Result(list[str]):
    end_status = ResultAttr[EndStatus]()
    event = ResultAttr[Hotkey | FzfEvent]()
    query = ResultAttr[str]()

    def __init__(self) -> None:
        self.exception: ExpectedException | None = None
        super().__init__()

    def __str__(self) -> str:
        return json.dumps({"status": self.end_status, "event": self.event, "query": self.query, "selections": self})


# TODO: Ability to output preview in Result (or anything else)
# TODO: id should be replaced in fzf options with commands in them that work with stored PromptData

# TODO: how to get current preview command so that updating data also updates current preview output?
# TODO: caching?
# TODO: preview should try to read from prompt data instead of calculating the output again
# TODO: store all line identities for easy transformations of lines?

# TODO: ❗ hotkey conflicts
# TODO: return to previous selection
# TODO: return with previous query
# TODO: Allow multiselect (multioutput)?
# TODO: How to include --bind hotkeys (internal fzf prompt actions)? Maybe action menu can just serve as a hotkey hint
# Decorator to turn a function into a script that is then used with --bind 'hotkey:execute(python script/path {q} {+})'
# TODO: enter action in ActionMenu
# TODO: hotkeys only in ActionMenu prompt (not consumed in owner prompt)
# TODO: Instead of interpreting falsey values as reset, there should be an explicit named exception raised and caught
# TODO: Sort actions
# TODO: Show action menu as preview (to see hotkeys without restarting prompt)
# TODO: Make action_menu_hotkey owned by ActionMenu instead of prompt
# TODO: Will subclasses need more than just define actions? Maybe some more options can be overridden?
# TODO: Preview of result
# TODO: ❗ Remake as an hotkey:execute(action_menu_prompt <prompt id (port #)>)
# TODO: - How to invoke it through --bind and recreate the action back in the owner prompt?
# TODO: Show command in fzf prompt (invoke using a hotkey maybe?)
# TODO: replace_prompt: bool = False
# TODO: silent: bool = True
# TODO: enforce post-process actions to end prompt


class ShellCommand(ParametrizedOptionString):
    ...


class ParametrizedAction(ParametrizedOptionString):
    ...


ShellCommandActionType = Literal["execute", "execute-silent", "change-preview"]
AnyShellCommand = TypeVar("AnyShellCommand", bound=ShellCommand)
AnyParametrizedAction = TypeVar("AnyParametrizedAction", bound=ParametrizedAction)


# raw fzf actions that aren't parametrized or name of preset action
BaseAction = Literal[
    "accept",
    "abort",
    "up",
    "down",
    "clear-query",
    "toggle-all",
    "select-all",
    "refresh-preview",
]
# Action can just be a string if you know what you're doing (look in `man fzf` for what can be assigned to '--bind')
Action = BaseAction | ParametrizedAction | tuple[ShellCommand, ShellCommandActionType]

# native fzf options may be overwritten here
PRESET_ACTIONS = {
    "accept": lambda: PromptEndingAction("accept"),
    "abort": lambda: PromptEndingAction("abort"),
}


class Binding:
    def __init__(self, name: str, /, *actions: Action | ShellCommand):
        """❗ Careful about mutating actions before they're passed into Binding constructor as those mutations are lost"""
        self.name = name  # only descriptive function
        # Ensure a new binding also has new unresolved actions
        self.actions: list[Action] = []
        for action in actions:
            if isinstance(action, ShellCommand):
                action = (action, "execute")
            if isinstance(action, tuple):
                self.actions.append((action[0].new_copy(), action[1]))
            elif isinstance(action, ParametrizedAction):
                self.actions.append(action.new_copy())
            elif isinstance(action, str) and (preset_action_factory := PRESET_ACTIONS.get(action)):
                self.actions.append(preset_action_factory())
            else:
                self.actions.append(action)

    @property
    def prompt_ending_action_count(self) -> int:
        return len(self.parametrized_actions(PromptEndingAction))

    def to_action_string(self) -> str:
        if self.prompt_ending_action_count > 1:
            # TODO: Allow multiple prompt-ending actions
            raise RuntimeError(f"Multiple prompt-ending actions disallowed ({self.prompt_ending_action_count})")
        try:
            action_strings = [
                f"{action[1]}({action[0].to_action_string()})"
                if isinstance(action, tuple)
                else action.to_action_string()
                if isinstance(action, (ParametrizedAction))
                else action
                for action in self.actions
            ]
        except RuntimeError as e:
            raise RuntimeError(f"{self.name}: {e}") from e
        return "+".join(action_strings)

    # TODO: Combine post_processors
    def __add__(self, other: Self) -> Self:
        return self.__class__(f"{self.name}+{other.name}", *(self.actions + other.actions))

    def __str__(self) -> str:
        actions = [f"'{str(action)}'" for action in self.actions]
        return f"{self.name}: {' -> '.join(actions)}"

    def shell_command_actions(
        self, shell_command_type: Type[AnyShellCommand]
    ) -> list[tuple[AnyShellCommand, ShellCommandActionType]]:
        return [
            (action[0], action[1])
            for action in self.actions
            if isinstance(action, tuple) and isinstance(action[0], shell_command_type)
        ]

    def parametrized_actions(
        self, parametrized_action_type: Type[AnyParametrizedAction]
    ) -> list[AnyParametrizedAction]:
        return [action for action in self.actions if isinstance(action, parametrized_action_type)]


ACCEPT_HOTKEY: Hotkey = "enter"
ABORT_HOTKEY: Hotkey = "esc"


class ActionMenu:
    def __init__(self) -> None:
        self.bindings: dict[Hotkey | FzfEvent, Binding] = {}
        self.post_processors: dict[Hotkey | FzfEvent, PostProcessor] = {}
        self.add(ACCEPT_HOTKEY, Binding("accept", "accept"))
        self.add(ABORT_HOTKEY, Binding("abort", "abort"))
        self.automator = Automator(self)
        self.to_automate: list[Binding | Hotkey] = []

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def shell_command_actions(
        self, shell_command_type: Type[AnyShellCommand]
    ) -> list[tuple[AnyShellCommand, ShellCommandActionType]]:
        return [
            action for binding in self.bindings.values() for action in binding.shell_command_actions(shell_command_type)
        ]

    def parametrized_actions(
        self, parametrized_action_type: Type[AnyParametrizedAction]
    ) -> list[AnyParametrizedAction]:
        return [
            action
            for binding in self.bindings.values()
            for action in binding.parametrized_actions(parametrized_action_type)
        ]

    def add(self, event: Hotkey | FzfEvent, binding: Binding):
        if event in self.bindings:
            raise RuntimeError(f"Hotkey conflict ({event}): {binding.name} vs {self.bindings[event].name}")
        self.bindings[event] = binding
        for action in binding.actions:
            if isinstance(action, PromptEndingAction):
                if action.post_processor:
                    self.post_processors[event] = action.post_processor
                action.resolve_event(event)

    # TODO: silent binding (doesn't appear in header help)?
    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.to_action_string())
        header_help = "\n".join(f"{event}\t{action.name}" for event, action in self.bindings.items())
        if self.should_run_automator:
            options.listen()
        return options.header(header_help).header_first

    @single_use_method
    def apply_post_processor(self, prompt_data: PromptData):
        if post_processor := self.post_processors.get(prompt_data.result.event):
            post_processor(prompt_data)

    def automate(self, *to_automate: Binding | Hotkey):
        self.to_automate.extend(to_automate)

    def automate_actions(self, *actions: Action):
        self.automate(Binding("anonymous actions", *actions))

    @property
    def should_run_automator(self) -> bool:
        return bool(self.to_automate)


# TODO: Can be invoked as prompt (like old action menu) in a subshell
# TODO: Custom automation can be used to invoke customized commands such as put(...)
class Automator(Thread):
    @property
    def port(self) -> str:
        if self.__port is None:
            raise RuntimeError("port not set")
        return self.__port

    @port.setter
    def port(self, value: str):
        self.__port = value
        logger.info(f"Automator listening on port {self.port}")

    def __init__(self, action_menu: ActionMenu) -> None:
        self.__port: str | None = None
        self.bindings: list[Binding] = []
        self.port_resolved = Event()
        self.binding_executed = Event()
        self.move_to_next_binding_server_call = ServerCall(self.move_to_next_binding)
        super().__init__()

    def run(self):
        try:
            while not self.port_resolved.is_set():
                if not self.port_resolved.wait(timeout=5):
                    logger.warning("Waiting for port to be resolved…")
            for binding_to_automate in self.bindings:
                binding = Binding(f"{binding_to_automate.name}+move to next binding")
                # HACK: PromptEndingAction won't allow move_to_next_binding_server_call to be called but that doesn't
                # matter because PromptEndingAction ends prompt anyway
                binding.actions = binding_to_automate.actions + [(self.move_to_next_binding_server_call, "execute")]
                self.execute_binding(binding)
        except Exception as e:
            logger.exception(e)
            raise

    def add_bindings(self, *bindings: Binding):
        self.bindings.extend(bindings)

    def execute_binding(self, binding: Binding):
        logger.debug(f"Automating {binding}")
        action_str = binding.to_action_string()
        self.binding_executed.clear()
        if response := shell_command(shlex.join(["curl", "-XPOST", f"localhost:{self.port}", "-d", action_str])):
            if not response.startswith("unknown action:"):
                logger.weirdness(response)
            raise RuntimeError(response)
        self.binding_executed.wait()
        time.sleep(0.3)

    def move_to_next_binding(self, prompt_data: PromptData):
        self.binding_executed.set()

    def resolve(self, action_menu: ActionMenu):
        action_menu.add("start", Binding("get automator port", ServerCall(self.get_port_number)))
        self.add_bindings(*[x if isinstance(x, Binding) else action_menu.bindings[x] for x in action_menu.to_automate])

    def get_port_number(self, prompt_data: PromptData, FZF_PORT: str):
        """Utilizes the $FZF_PORT variable containing the port assigned to --listen option
        (or the one generated automatically when --listen=0)"""
        self.port = FZF_PORT
        clipboard.copy(FZF_PORT)
        self.port_resolved.set()


class Request(pydantic.BaseModel):
    server_call_name: str
    args: list = []
    kwargs: dict = {}


PLACEHOLDERS = {
    "query": "--arg query {q}",  # type str
    "selection": "--arg selection {}",  # type str
    "selections": "--argjson selections \"$(jq --compact-output --null-input '$ARGS.positional' --args {+})\"",  # type list[str]
    "index": "--argjson index {n}",  # type int
    "indices": "--argjson indices \"$(jq --compact-output --null-input '[$ARGS.positional[] | tonumber]' --args {+n})\"",  # type list[int]
}


class CommandOutput(str):
    ...


P = ParamSpec("P")
R = TypeVar("R", bound=str | None)
# means it requires first paramketer to be of type PromptData but other parameters can be anything
ServerCallFunction = Callable[Concatenate["PromptData", P], R]


# TODO: Add support for index {n} and indices {+n}
# TODO: Will logging slow it down too much?
# TODO: Allow seeing output of server call and wait for key press to return to prompt
class ServerCall(ShellCommand):
    """❗ custom name mustn't have single nor double quotes in it. It only has informative purpose anyway"""

    def __init__(self, function: ServerCallFunction, custom_name: str | None = None) -> None:
        self.function = function
        self.name = f"{custom_name or function.__name__} ({id(self)})"
        self.socket_number: int

        parameters = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
        jq_args = []
        placeholders_to_resolve = []
        for parameter in parameters:
            if placeholder := PLACEHOLDERS.get(parameter.name):
                jq_args.append(placeholder)
            elif isinstance(parameter.default, CommandOutput):
                jq_args.append(f'--arg {parameter.name} "$({parameter.default})"')
            else:
                # to be replaced using .resolve or is an environment variable
                jq_args.append(f'--arg {parameter.name} "${parameter.name}"')
                # environmental variables are recognized by being all uppercase
                if not re.match("^[A-Z_]*$", parameter.name):
                    placeholders_to_resolve.append(parameter.name)
        template = (
            'jq --null-input --compact-output \'{"server_call_name":"'
            + self.name
            + '","kwargs":$ARGS.named}\' '
            + " ".join(jq_args)
            + " | nc localhost $socket_number"
        )
        placeholders_to_resolve.append("socket_number")
        super().__init__(template, placeholders_to_resolve)

    @single_use_method
    def resolve_socket_number(self, socket_number: int) -> None:
        self.socket_number = socket_number
        self.resolve(socket_number=socket_number)


class PostProcessor(Protocol):
    __name__: str

    @staticmethod
    def __call__(prompt_data: PromptData) -> None:
        ...


EMPTY_SELECTIONS = [""]


class PromptEndingAction(ParametrizedAction):
    def __init__(self, end_status: EndStatus, post_processor: PostProcessor | None = None) -> None:
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self.event: Hotkey | FzfEvent
        self.pipe_call = ServerCall(self.pipe_results)
        super().__init__("execute-silent($pipe_call)+abort", ["pipe_call"])

    def pipe_results(self, prompt_data: PromptData, event: Hotkey | FzfEvent, query: str, selections: list[str]):
        prompt_data.result.query = query
        prompt_data.result.event = event
        prompt_data.result.end_status = self.end_status
        if selections != EMPTY_SELECTIONS:
            prompt_data.result.extend(selections)
        logger.debug("Piping results")
        logger.debug(prompt_data.result)

    @single_use_method
    def resolve_event(self, event: Hotkey | FzfEvent):
        self.event = event
        self.pipe_call.resolve(event=event)

    def to_action_string(self) -> str:
        if not self.resolved:
            self.resolve(pipe_call=self.pipe_call.to_action_string())
        return super().to_action_string()


class Server(Thread):
    def __init__(self, prompt_data: PromptData, server_setup_finished: Event, server_should_close: Event) -> None:
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.server_setup_finished = server_setup_finished
        self.server_should_close = server_should_close
        self.server_calls: dict[str, ServerCall] = {sc.name: sc for sc in prompt_data.server_calls()}

    # TODO: Use automator to end running prompt and propagate errors
    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(("localhost", 0))
                socket_specs = server_socket.getsockname()
                socket_number = socket_specs[1]
                self.resolve_all_server_calls(socket_number)
                server_socket.listen()
                logger.info(f"Server listening on {socket_specs}...")

                self.server_setup_finished.set()
                server_socket.settimeout(0.05)
                while True:
                    try:
                        client_socket, addr = server_socket.accept()
                    except TimeoutError:
                        if self.server_should_close.is_set():
                            logger.info(f"Server closing with result: {self.prompt_data.result}")
                            break
                        continue
                    logger.info(f"Connection from {addr}")
                    self.handle_request(client_socket, self.prompt_data)
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            self.server_setup_finished.set()

    def handle_request(self, client_socket: socket.socket, prompt_data: PromptData):
        payload = bytearray()
        while r := client_socket.recv(1024):
            payload.extend(r)
        try:
            request = Request.model_validate_json(payload.decode("utf-8").strip())
            logger.debug(request.server_call_name)
            function = self.server_calls[request.server_call_name].function
            response = function(prompt_data, *request.args, **request.kwargs)
        except ExpectedException as e:
            prompt_data.result.exception = e
            self.server_should_close.set()
            return
        except Exception:
            response = traceback.format_exc()
        if response:
            client_socket.sendall(response.encode("utf-8"))
        client_socket.close()

    def resolve_all_server_calls(self, socket_number: int):
        for server_call in self.server_calls.values():
            server_call.resolve_socket_number(socket_number)


PreviewFunction = ServerCallFunction[P, str]


@dataclass
class Preview:
    # TODO: | Event
    # TODO: implement ServerCall commands
    def __init__(
        self,
        name: str,
        command: str | PreviewFunction,
        hotkey: Hotkey,
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        self.name = name
        self.command = (
            ShellCommand(command)
            if isinstance(command, str) and not store_output
            else PreviewChangeServerCall(command, name, store_output)
        )
        self.hotkey: Hotkey = hotkey
        self.window_size = window_size
        self.window_position: Position = window_position
        self.preview_label = preview_label
        self.output: str


class PreviewChangeServerCall(ServerCall):
    def __init__(self, command: str | PreviewFunction, name: str, store_output: bool) -> None:
        if isinstance(command, str):

            def execute_preview(prompt_data: PromptData, preview_output: str = CommandOutput("echo $preview_output")):
                prompt_data.previewer.current_preview = prompt_data.previewer.previews[name]
                if store_output:
                    prompt_data.previewer.previews[name].output = preview_output
                logger.trace(f"Changing preview to '{name}'", preview=name)

            super().__init__(execute_preview, f"Execute preview {name}")
            self.template = f"preview_output=$({command}) && echo $preview_output && {self.template}"
        else:

            def execute_preview_with_enclosed_function(prompt_data: PromptData, **kwargs):
                prompt_data.previewer.current_preview = prompt_data.previewer.previews[name]
                logger.trace(f"Changing preview to '{name}'", preview=name)
                preview_output = command(prompt_data, **kwargs)
                if store_output:
                    prompt_data.previewer.previews[name].output = preview_output
                return preview_output

            super().__init__(command, f"Execute preview {name}")
            self.function = execute_preview_with_enclosed_function  # HACK


class PreviewWindowChange(ParametrizedAction):
    def __init__(self, window_size: int | str, window_position: Position) -> None:
        """Window size: int - absolute, str - relative and should be in '<int>%' format"""
        self.window_size = window_size
        self.window_position = window_position
        super().__init__(f"change-preview-window({self.window_size},{self.window_position})")


class Previewer:
    """Handles passing right preview options"""

    def __init__(self) -> None:
        self.previews: dict[str, Preview] = {}
        self.current_preview: Preview | None = None

    def add(self, preview: Preview, action_menu: ActionMenu, *, main: bool = False):
        if main or self.current_preview is None:
            self.current_preview = preview
        self.previews[preview.name] = preview
        action_menu.add(
            preview.hotkey,
            # It's crucial that window change happens before preview change (see )
            Binding(
                f"Change preview to '{preview.name}'",
                PreviewWindowChange(preview.window_size, preview.window_position),
                (preview.command, "change-preview"),
                "refresh-preview",
            ),
        )

    def resolve_options(self) -> Options:
        if self.current_preview is None:  # Meaning no preview was added
            return Options()
        return (
            Options()
            .preview(self.current_preview.command.to_action_string())
            .preview_window(self.current_preview.window_position, self.current_preview.window_size)
        )


JSON_ENV_VAR_NAME = "PROMPT_DATA"


@dataclass
class PromptData:
    """Accessed from fzf process through socket Server"""

    id: str = field(init=False, default_factory=lambda: datetime.now().isoformat())  # TODO: use or remove
    choices: Iterable = field(default_factory=list)
    previewer: Previewer = field(default_factory=Previewer)
    action_menu: ActionMenu = field(default_factory=ActionMenu)
    options: Options = field(default_factory=Options)
    data: dict = field(default_factory=dict)  # arbitrary data to be accessed
    data_as_env_var: bool = False
    result: Result = field(init=False, default_factory=Result)

    def get_current_preview(self) -> str:
        if not self.previewer.current_preview:
            raise RuntimeError("No current preview")
        return self.previewer.current_preview.output

    def add_preview(self, preview: Preview, *, main: bool = False):
        self.previewer.add(preview, self.action_menu, main=main)

    @single_use_method
    def resolve_options(self) -> Options:
        return self.options + self.previewer.resolve_options() + self.action_menu.resolve_options()

    def server_calls(self) -> list[ServerCall]:
        server_calls = [action[0] for action in self.action_menu.shell_command_actions(ServerCall)]
        server_calls.extend(action.pipe_call for action in self.action_menu.parametrized_actions(PromptEndingAction))
        server_calls.extend(
            preview.command for preview in self.previewer.previews.values() if isinstance(preview.command, ServerCall)
        )
        if self.action_menu.should_run_automator:
            server_calls.append(self.action_menu.automator.move_to_next_binding_server_call)
        return server_calls


if __name__ == "__main__":
    pass
