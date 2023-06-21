# Black magic layer
from __future__ import annotations

import inspect
import json
import shlex
import socket
import subprocess
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from shutil import which
from string import Template
from threading import Event, Thread
from typing import Any, Callable, Concatenate, Generic, Literal, NoReturn, ParamSpec, Protocol, Self, TypeVar
import clipboard

import pydantic
from thingies import shell_command

from ..monitoring.Logger import get_logger
from .commands.fzf_placeholders import PLACEHOLDERS
from .exceptions import ExpectedException
from .options import FzfEvent, Hotkey, Options, Position

logger = get_logger()
ACCEPT_HOTKEY: Hotkey = "enter"
ABORT_HOTKEY: Hotkey = "esc"

FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Unbind some default fzf hotkeys (add bind 'hk:ignore' options from left)
# TODO: Solve other expected hotkeys
# TODO: Use tempfile
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable specified in vscode-insiders://file/Users/honza/.dotfiles/.zshforfzf:4
def run_fzf_prompt(prompt_data: PromptData, *, executable_path=None) -> Result:
    if not which("fzf") and not executable_path:
        raise SystemError(f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")
    else:
        executable_path = "fzf"

    server_setup_finished = Event()
    server_should_close = Event()
    server = Server(prompt_data, server_setup_finished, server_should_close)
    server.start()
    server_setup_finished.wait()

    options = prompt_data.resolve_options()
    logger.debug("\n".join(options.options))

    if prompt_data.action_menu.automator.to_execute:
        prompt_data.action_menu.automator.start()

    # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
    # TODO: 🧊 Use subprocess.run without shell=True (need to change Options)
    try:
        subprocess.run(
            f"{executable_path} {options}",
            shell=True,
            input="\n".join(str(choice) for choice in prompt_data.choices).encode(),
            check=True,
        )
    except subprocess.CalledProcessError as err:
        if err.returncode != 130:  # 130 means aborted
            raise
    finally:
        server_should_close.set()
    server.join()
    if isinstance(e := prompt_data.result.exception, ExpectedException):
        raise e
    return prompt_data.action_menu.get_result(prompt_data)
    # result = Result(FzfPrompt(executable_path).prompt(prompt_data.choices, str(options), delimiter))
    # return prompt_data.action_menu.process_result(result)


T = TypeVar("T")


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


class ShellCommand:
    def __init__(self, value: str) -> None:
        self.value = value

    # TODO: check finalization for easier testing
    def safe_substitute(self, mapping: dict) -> None:
        """replaces $key present in .command with value"""
        self.value = Template(self.value).safe_substitute(mapping)

    def __str__(self) -> str:
        return self.value


class ParametrizedAction(ABC):
    @abstractmethod
    def __str__(self) -> str:
        """To resolve into fzf options"""


class PostProcessor(Protocol):
    __name__: str

    @staticmethod
    def __call__(prompt_data: PromptData) -> Result | NoReturn:
        ...


class PostProcessAction:
    """Requires program to know what event happened (what hotkey was pressed)"""

    def __init__(self, post_processor: PostProcessor) -> None:
        self.post_processor = post_processor

    def __str__(self) -> str:
        return self.post_processor.__name__


class Binding:
    def __init__(self, name: str, /, *actions: Action, end_prompt: PromptEndingAction | Literal[False] = False):
        self.name = name
        self.actions: list[Action] = list(actions)
        self.end_prompt: PromptEndingAction | Literal[False] = end_prompt
        post_process_action_count = sum(isinstance(action, PostProcessAction) for action in actions)
        if post_process_action_count > 0 and not self.end_prompt:
            raise RuntimeError("Post-process action needs prompt to end")
        if post_process_action_count > 1:
            raise RuntimeError(f"Multiple post-process actions disallowed ({post_process_action_count})")

    def resolve(self) -> str:
        action_strings = [
            f"execute({action})" if isinstance(action, ShellCommand) else str(action)
            for action in self.actions
            if not isinstance(action, PostProcessAction)
        ]
        if self.end_prompt:
            action_strings.append("abort")
        return "+".join(action_strings)

    def __str__(self) -> str:
        actions = [f"'{str(action)}'" for action in self.actions]
        return f"{self.name}: {' -> '.join(actions)}"

    def __add__(self, other: Self) -> Self:
        self.actions.extend(other.actions)
        self.name = f"{self.name}+{other.name}"
        self.end_prompt = self.end_prompt
        return self


PromptEndingAction = Literal["accept", "abort"]


class Result(list[str]):
    end_status = ResultAttr[PromptEndingAction]()
    event = ResultAttr[Hotkey | FzfEvent]()
    query = ResultAttr[str]()

    def __init__(self) -> None:
        self.exception: ExpectedException | None = None
        super().__init__()

    def __str__(self) -> str:
        return json.dumps({"status": self.end_status, "event": self.event, "query": self.query, "selections": self})


class ActionMenu:
    def __init__(self) -> None:
        self.bindings: dict[Hotkey | FzfEvent, Binding] = {}
        self.post_processors: dict[Hotkey | FzfEvent, PostProcessor] = {}
        self.add("enter", Binding("accept", end_prompt="accept"))
        self.add("esc", Binding("abort", end_prompt="abort"))
        self.automator = Automator(self)
        self.add("start", Binding("get automator port", ServerCall(self.automator.get_port_number)))

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(self, event: Hotkey | FzfEvent, binding: Binding):
        if event in self.bindings:
            raise RuntimeError(f"Hotkey conflict ({event}): {binding.name} vs {self.bindings[event].name}")
        self.bindings[event] = binding
        for action in binding.actions:
            if isinstance(action, PostProcessAction):
                self.post_processors[event] = action.post_processor
        if binding.end_prompt:
            end_status = binding.end_prompt

            def pipe_results(prompt_data: PromptData, query: str, selections: list[str]):
                prompt_data.result.query = query
                prompt_data.result.event = event
                prompt_data.result.end_status = end_status
                prompt_data.result.extend(selections)
                logger.debug("Piping results")
                logger.debug(prompt_data.result)

            server_call_name = f"pipe results ({event})"
            binding.actions.append(ServerCall(pipe_results, server_call_name))

    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.resolve())
        header_help = "\n".join(f"{event}\t{action.name}" for event, action in self.bindings.items())
        return options.header(header_help).header_first + self.automator.resolve_options()

    def get_result(self, prompt_data: PromptData):
        post_processor = self.post_processors.get(prompt_data.result.event)
        return post_processor(prompt_data) if post_processor else prompt_data.result

    def automate(self, *to_execute: Binding | Hotkey):
        self.automator.add_bindings(*to_execute)

    def automate_actions(self, *actions: Action):
        self.automate(Binding("anonymous actions", *actions))


PRESET_ACTIONS = {}
# raw fzf actions that aren't parametrized or name of preset action
BaseAction = Literal[
    "up",
    "down",
    "clear-query",
    "toggle-all",
    "select-all",
    "refresh-preview",
]
# Action can just be a string if you know what you're doing (look in `man fzf` for what can be assigned to '--bind')
Action = BaseAction | ParametrizedAction | PostProcessAction | ShellCommand


# BUG: Sending 'change-preview' action doesn't make the preview "stick"
# in  the sense that any other action that causes preview to update reverts the preview back
# to the original preview (the one defined using --preview option);
# therefore checking changes in preview using automated prompt is not advised
# - sending actions is non-blocking
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
        self._action_menu = action_menu
        self.to_execute: list[Binding | Hotkey] = []
        self.starting_signal = Event()
        self.binding_executed = Event()
        self.move_to_next_binding_server_call = ServerCall(self.move_to_next_binding)
        super().__init__()

    def run(self):
        try:
            self.starting_signal.wait()
            for binding in [x if isinstance(x, Binding) else self._action_menu.bindings[x] for x in self.to_execute]:
                self.execute_binding(binding + Binding("move to next binding", self.move_to_next_binding_server_call))
        except Exception as e:
            logger.exception(e)
            raise

    def add_bindings(self, *bindings: Binding | Hotkey):
        self.to_execute.extend(bindings)

    def execute_binding(self, binding: Binding):
        logger.debug(f"Automating {binding}")
        action_str = binding.resolve()
        self.binding_executed.clear()
        if response := shell_command(shlex.join(["curl", "-XPOST", f"localhost:{self.port}", "-d", action_str])):
            if not response.startswith("unknown action:"):
                logger.weirdness(response)
            raise RuntimeError(response)
        self.binding_executed.wait()
        time.sleep(0.3)

    def move_to_next_binding(self, prompt_data: PromptData):
        self.binding_executed.set()

    def resolve_options(self) -> Options:
        return Options().listen()

    def get_port_number(self, prompt_data: PromptData, FZF_PORT: str):
        """Utilizes the $FZF_PORT variable containing the port assigned to --listen option
        (or the one generated automatically when --listen=0)"""
        self.port = FZF_PORT
        clipboard.copy(FZF_PORT)
        self.starting_signal.set()


class PreviewFunction(Protocol):
    @staticmethod
    def __call__(query: str, selection: str, selections: list[str]) -> str:
        ...


@dataclass
class Preview:
    # TODO: | Event
    # TODO: implement ServerCall commands
    def __init__(
        self,
        name: str,
        command: str,
        hotkey: Hotkey,
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        self.name = name
        self.hotkey: Hotkey = hotkey
        self.window_size = window_size
        self.window_position: Position = window_position
        self.preview_label = preview_label
        self.output: str

        if store_output:

            def execute_preview(
                prompt_data: PromptData,
                preview_name: str,
                # preview_output: str = CommandOutput(command),
                preview_output: str = CommandOutput("echo $preview_output"),
            ):
                prompt_data.previewer.current_preview = prompt_data.previewer.previews[preview_name]
                prompt_data.previewer.previews[preview_name].output = preview_output
                # return preview_output

            self.command = ServerCall(execute_preview, f"Execute preview {self.name}")
            self.command.value = f"preview_output=$({command}) && echo $preview_output && {self.command.value}"
            self.command.safe_substitute({"preview_name": self.name})
        else:
            self.command = command


class PreviewChange(ParametrizedAction):
    def __init__(self, preview: Preview) -> None:
        self.shell_command = preview.command

    def __str__(self) -> str:
        return f"change-preview({self.shell_command})"


class PreviewWindowChange(ParametrizedAction):
    def __init__(self, window_size: int | str, window_position: Position) -> None:
        self.window_size = window_size
        self.window_position = window_position

    def __str__(self) -> str:
        return f"change-preview-window({self.window_size},{self.window_position})"


class Previewer:
    """Handles passing right preview options"""

    def __init__(self) -> None:
        self.previews: dict[str, Preview] = {}
        self.current_preview: Preview | None = None

    def add(self, preview: Preview, action_menu: ActionMenu, main: bool = False):
        if main or self.current_preview is None:
            self.current_preview = preview
        self.previews[preview.name] = preview
        action_menu.add(
            preview.hotkey,
            Binding(
                f"Change preview to '{preview.name}'",
                PreviewChange(preview),
                PreviewWindowChange(preview.window_size, preview.window_position),
                "refresh-preview",
            ),
        )

    def resolve_options(self) -> Options:
        if self.current_preview is None:  # Meaning no preview was added
            return Options()

        options = (
            Options()
            .preview(str(self.current_preview.command))
            .preview_window(self.current_preview.window_position, self.current_preview.window_size)
        )

        # for preview_name, preview in self.previews.items(): # TODO: attach change preview hotkey
        #     options.bind(preview.hotkey, f"execute({RequestCommand(preview_name, socket_number)})")
        return options


@dataclass
class PromptData:
    """Accessed through socket Server"""

    id: str = field(init=False, default_factory=lambda: datetime.now().isoformat())
    choices: list = field(default_factory=list)
    previewer: Previewer = field(default_factory=Previewer)
    action_menu: ActionMenu = field(default_factory=ActionMenu)
    options: Options = field(default_factory=Options)
    result: Result = field(init=False, default_factory=Result)

    def get_current_preview(self) -> str:
        if not self.previewer.current_preview:
            raise RuntimeError("No current preview")
        return self.previewer.current_preview.output

    def add_preview(self, preview: Preview):
        self.previewer.add(preview, self.action_menu)

    def resolve_options(self) -> Options:
        return self.options + self.previewer.resolve_options() + self.action_menu.resolve_options()


class Request(pydantic.BaseModel):
    server_call_name: str
    args: list = []
    kwargs: dict = {}


PLACEHOLDERS = {
    "query": "--arg query {q}",
    "selection": "--arg selection {}",
    "selections": "--argjson selections \"$(jq --compact-output --null-input '$ARGS.positional' --args {+})\"",
    "index": "--arg selection {n}",
    "indices": "--argjson selections \"$(jq --compact-output --null-input '$ARGS.positional' --args {+n})\"",
}


class CommandOutput(str):
    ...


def get_json_creating_command(function: Callable) -> str:
    parameters = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
    jq_args = []
    for parameter in parameters:
        if placeholder := PLACEHOLDERS.get(parameter.name):
            jq_args.append(placeholder)
        elif isinstance(parameter.default, CommandOutput):
            jq_args.append(f'--arg {parameter.name} "$({parameter.default})"')
        else:
            # to be replaced using string.Template.safe_substitute or is an environment variable
            jq_args.append(f'--arg {parameter.name} "${parameter.name}"')

    return (
        'jq --null-input --compact-output \'{"server_call_name":"$server_call_name", "kwargs":$ARGS.named}\' '
        + " ".join(jq_args)
    )


P = ParamSpec("P")
ServerCallFunction = Callable[Concatenate[PromptData, P], Any]


# TODO: Add support for index {n} and indices {+n}
# TODO: Will logging slow it down too much?
class ServerCall(ShellCommand):
    """❗ custom name mustn't have single quotes in it. It only serves to distinguish functions anyway"""

    def __init__(self, function: ServerCallFunction, name: str | None = None) -> None:
        self.function = function
        self.name = name or function.__name__
        self.resolved = False
        super().__init__(Template(get_json_creating_command(function)).safe_substitute({"server_call_name": self.name}))

    def resolve(self, socket_number: int) -> None:
        self.value = f"{self.value} | nc localhost {socket_number}"
        self.resolved = True

    def __str__(self) -> str:
        if not self.resolved:
            raise RuntimeError(f"{self.name} not resolved")
        return super().__str__()


class Server(Thread):
    def __init__(
        self,
        prompt_data: PromptData,
        server_setup_finished: Event,
        server_should_close: Event,
    ) -> None:
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.server_setup_finished = server_setup_finished
        self.server_should_close = server_should_close
        self.server_calls: dict[str, ServerCall] = (
            {action.name: action for action in prompt_data.action_menu.actions if isinstance(action, ServerCall)}
            | {
                preview.command.name: preview.command
                for preview in prompt_data.previewer.previews.values()
                if isinstance(preview.command, ServerCall)
            }
            | {
                prompt_data.action_menu.automator.move_to_next_binding_server_call.name: prompt_data.action_menu.automator.move_to_next_binding_server_call
            }
        )

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

    def handle_request(self, client_socket: socket.socket, prompt_data: PromptData):
        payload = bytearray()
        while r := client_socket.recv(1024):
            payload.extend(r)
        try:
            request = pydantic.parse_raw_as(Request, payload.decode("utf-8").strip())
            f = self.server_calls[request.server_call_name].function
            logger.debug(request.server_call_name)
            response = f(prompt_data, *request.args, **request.kwargs)
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
            server_call.resolve(socket_number)


if __name__ == "__main__":
    pass
