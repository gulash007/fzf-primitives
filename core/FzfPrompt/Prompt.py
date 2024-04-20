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
from datetime import datetime
from shutil import which
from threading import Event, Thread
from typing import Callable, Concatenate, Iterable, Literal, ParamSpec, Self, TypeVar

import clipboard
import pydantic
import requests
from thingies.shell import MoreInformativeCalledProcessError

from ..monitoring.Logger import get_logger
from .decorators import single_use_method
from .exceptions import ExitLoop
from .options import (
    BaseAction,
    Hotkey,
    Options,
    ParametrizedActionType,
    ParametrizedOptionString,
    Position,
    Situation,
    ShellCommandActionType,
)
from .shell import SHELL_SCRIPTS

T = TypeVar("T")

logger = get_logger()

FZF_URL = "https://github.com/junegunn/fzf"


# TODO: Unbind some default fzf hotkeys (add bind 'hk:ignore' options from left)
# TODO: Solve other expected hotkeys
# TODO: Use tempfile
# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable
def run_fzf_prompt[T, S](prompt_data: PromptData[T, S], *, executable_path=None) -> Result[T]:
    if not which("fzf") and not executable_path:
        raise SystemError(f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")
    else:
        executable_path = "fzf"

    if (action_menu := prompt_data.action_menu).should_run_automator:
        action_menu.automator.resolve(action_menu)
        action_menu.automator.start()

    if prompt_data.previewer.previews:
        initial_preview = prompt_data.previewer.current_preview
        prompt_data.action_menu.add(
            "start",
            Binding(
                f"Change preview to '{initial_preview.name}'",
                PreviewWindowChange(initial_preview.window_size, initial_preview.window_position),
                PreviewChange(initial_preview),
                (
                    ShellCommand(initial_preview.command, "change-preview")
                    if not initial_preview.store_output and isinstance(initial_preview.command, str)
                    else GetCurrentPreviewFromServer(initial_preview)
                ),
            ),
            conflict_resolution="prepend",
        )

    server_setup_finished = Event()
    server_should_close = Event()
    server = Server(prompt_data, server_setup_finished, server_should_close)
    server.start()
    server_setup_finished.wait()

    # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
    # TODO: 🧊 Use subprocess.run without shell=True as [executable_path, *options] (need to change Options)
    try:
        options = prompt_data.resolve_options()
        logger.debug(f"Running fzf with options:\n{options.pretty()}")
        subprocess.run(
            [executable_path, *shlex.split(str(options))],
            shell=False,
            input=prompt_data.choices_string.encode(),
            check=True,
            env=os.environ | {JSON_ENV_VAR_NAME: json.dumps(prompt_data.data)} if prompt_data.data_as_env_var else None,
        )
    except subprocess.CalledProcessError as err:
        # 130 means aborted or unassigned hotkey was pressed
        # TODO: Disable those hotkeys instead
        if err.returncode != 130:
            raise MoreInformativeCalledProcessError(err)
    finally:
        server_should_close.set()
    server.join()
    if not prompt_data.finished:
        # TODO: This may be explicitly allowed in the future (need to test when it's not)
        raise RuntimeError("Prompt not finished (you aborted prompt without finishing PromptData)")
    if prompt_data.result.end_status == "quit":
        raise ExitLoop(f"Exiting app with\n{prompt_data.result}")
    prompt_data.apply_common_post_processors(prompt_data)
    return prompt_data.result


EndStatus = Literal["accept", "abort", "quit"]


class Result(list[T]):
    def __init__(
        self,
        end_status: EndStatus,
        event: Hotkey | Situation,
        choices: list[T],
        query: str,  # as in {q} placeholder
        single_index: int | None,  # as in {n} placeholder
        indices: list[int],  # as in {+n} placeholder
        single_line: str | None,  # as in {} placeholder; stripped of ANSI codes
        lines: list[str],  # as in {+} placeholder; stripped of ANSI codes
    ):
        self.end_status: EndStatus = end_status
        self.event: Hotkey | Situation = event
        self.query = query
        self.single_index = single_index  # of pointer starting from 0
        self.indices = indices  # of marked selections or pointer if none are selected
        self.single = choices[single_index] if single_index is not None else None
        self.single_line = single_line  # pointed at
        self.lines = lines  # marked selections or pointer if none are selected
        super().__init__([choices[i] for i in indices])

    def __str__(self) -> str:
        return json.dumps(
            {
                "status": self.end_status,
                "event": self.event,
                "query": self.query,
                "single_index": self.single_index,
                "indices": self.indices,
                "selections": list(self),
                "single": self.single,
                "single_line": self.single_line,
                "lines": self.lines,
            },
            indent=4,
            default=repr,
        )


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


class ParametrizedAction(ParametrizedOptionString):

    def __init__(
        self, template: str, action_type: ParametrizedActionType, placeholders_to_resolve: Iterable[str] = ()
    ) -> None:
        self.action_type: ParametrizedActionType = action_type
        super().__init__(template, placeholders_to_resolve)

    def action_string(self) -> str:
        return f"{self.action_type}({self.resolved_string()})"


class ShellCommand(ParametrizedAction):
    def __init__(
        self,
        command_template: str,
        action_type: ShellCommandActionType = "execute",
        placeholders_to_resolve: Iterable[str] = (),
    ) -> None:
        super().__init__(command_template, action_type, placeholders_to_resolve)


# Action can just be a string if you know what you're doing (look in `man fzf` for what can be assigned to '--bind')
Action = BaseAction | ParametrizedAction


class Binding:
    def __init__(self, name: str, /, *actions: Action):
        self.name = name  # only descriptive function
        self.actions: list[Action] = []
        self.final_action: PromptEndingAction | None = None
        for action in actions:
            if self.final_action is not None:
                raise ValueError(f"{self.name}: PromptEndingAction should be the last action in the binding: {actions}")
            self.actions.append(action)
            if isinstance(action, PromptEndingAction):
                self.final_action = action

    def to_action_string(self) -> str:
        actions = self.actions.copy()
        if self.final_action:
            actions.append("abort")
        action_strings = [
            action.action_string() if isinstance(action, ParametrizedAction) else action for action in actions
        ]
        return "+".join(action_strings)

    def __add__(self, other: Self) -> Self:
        return self.__class__(f"{self.name}+{other.name}", *(self.actions + other.actions))

    def __str__(self) -> str:
        actions = [f"'{str(action)}'" for action in self.actions]
        return f"{self.name}: {' -> '.join(actions)}"


ConflictResolution = Literal["raise error", "override", "append", "prepend"]


class BindingConflict(Exception):
    pass


class ActionMenu[T, S]:
    def __init__(self, previewer: Previewer[T, S]) -> None:
        self.bindings: dict[Hotkey | Situation, Binding] = {}
        self.previewer = previewer
        self.automator = Automator()
        self.to_automate: list[Binding | Hotkey] = []

    @property
    def actions(self) -> list[Action]:
        return [action for binding in self.bindings.values() for action in binding.actions]

    def add(
        self, event: Hotkey | Situation, binding: Binding, *, conflict_resolution: ConflictResolution = "raise error"
    ):
        if binding.final_action:
            binding.final_action.resolve_event(event)
        if event not in self.bindings:
            self.bindings[event] = binding
        else:
            match conflict_resolution:
                case "raise error":
                    raise BindingConflict(f"Event {event} already has a binding: {self.bindings[event]}")
                case "override":
                    self.bindings[event] = binding
                case "append":
                    self.bindings[event] += binding
                case "prepend":
                    self.bindings[event] = binding + self.bindings[event]
                case _:
                    raise ValueError(f"Invalid conflict resolution: {conflict_resolution}")

    # TODO: silent binding (doesn't appear in header help)?
    @single_use_method
    def resolve_options(self) -> Options:
        options = Options()
        for event, binding in self.bindings.items():
            options.bind(event, binding.to_action_string())
        header_help = "\n".join(f"{event}\t{action.name}" for event, action in self.bindings.items())
        if self.should_run_automator:
            options.listen()
        return options.header(header_help).header_first

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

    def __init__(self) -> None:
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
                self.execute_binding(binding_to_automate)
        except Exception as e:
            logger.exception(e)
            raise

    def add_bindings(self, *bindings: Binding):
        self.bindings.extend(bindings)

    def execute_binding(self, binding: Binding):
        logger.debug(f"Automating {binding}")
        if not binding.final_action:
            binding += Binding("move to next automated binding", self.move_to_next_binding_server_call)
        action_str = (
            binding
            if binding.final_action
            else binding + Binding("move to next automated binding", self.move_to_next_binding_server_call)
        ).to_action_string()
        self.binding_executed.clear()
        if response := requests.post(f"http://localhost:{self.port}", data=action_str).text:
            if not response.startswith("unknown action:"):
                logger.weirdness(response)
            raise RuntimeError(response)
        if binding.final_action:
            return
        self.binding_executed.wait()
        time.sleep(0.4)

    def move_to_next_binding(self, prompt_data: PromptData):
        self.binding_executed.set()

    def resolve(self, action_menu: ActionMenu):
        action_menu.add(
            "start", Binding("get automator port", ServerCall(self.get_port_number)), conflict_resolution="prepend"
        )
        self.add_bindings(*[x if isinstance(x, Binding) else action_menu.bindings[x] for x in action_menu.to_automate])

    def get_port_number(self, prompt_data: PromptData, FZF_PORT: str):
        """Utilizes the $FZF_PORT variable containing the port assigned to --listen option
        (or the one generated automatically when --listen=0)"""
        self.port = FZF_PORT
        clipboard.copy(FZF_PORT)
        self.port_resolved.set()


class CommandOutput(str): ...


P = ParamSpec("P")
R = TypeVar("R", bound=str | None)
# means it requires first parameter to be of type PromptData but other parameters can be anything
type ServerCallFunctionGeneric[T, S, R] = Callable[Concatenate[PromptData[T, S], ...], R]
type ServerCallFunction[T, S] = ServerCallFunctionGeneric[T, S, str | None]


# TODO: Add support for index {n} and indices {+n}
# TODO: Will logging slow it down too much?
# TODO: Allow seeing output of server call and wait for key press to return to prompt
class ServerCall[T, S](ShellCommand):
    """❗ custom name mustn't have single nor double quotes in it. It only has informative purpose anyway"""

    def __init__(
        self,
        function: ServerCallFunction[T, S],
        custom_name: str | None = None,
        action_type: ShellCommandActionType = "execute",
    ) -> None:
        self.function = function
        self.name = custom_name or function.__name__
        self.id = f"{custom_name or function.__name__} ({id(self)})"
        self.socket_number: int

        template, placeholders_to_resolve = Request.create_template(self.id, function, action_type)
        placeholders_to_resolve.append("socket_number")
        super().__init__(template, action_type, placeholders_to_resolve)

    @single_use_method
    def resolve_socket_number(self, socket_number: int) -> None:
        self.socket_number = socket_number
        self.resolve(socket_number=socket_number)

    def __str__(self) -> str:
        return f"{self.id}: {super().__str__()}"


type PostProcessor[T, S] = Callable[[PromptData[T, S]], None]


class PromptEndingAction[T, S](ServerCall):
    def __init__(self, end_status: EndStatus, post_processor: PostProcessor[T, S] | None = None) -> None:
        self.end_status: EndStatus = end_status
        self.post_processor = post_processor
        self._event: Hotkey | Situation | None = None
        # ❗ Needs to be silent, otherwise program can get stuck when waiting for user input on error in Server
        super().__init__(self.pipe_results, action_type="execute-silent")

    @property
    def event(self) -> Hotkey | Situation:
        if self._event is None:
            raise RuntimeError("event not resolved")
        return self._event

    def pipe_results(self, prompt_data: PromptData[T, S], event: Hotkey | Situation):
        prompt_data.finish(event, self.end_status)
        if self.post_processor:
            self.post_processor(prompt_data)
        logger.debug(f"Piping results:\n{prompt_data.result}")

    @single_use_method
    def resolve_event(self, event: Hotkey | Situation):
        self._event = event
        self.resolve(event=event)

    def __str__(self) -> str:
        event = self.event if self._event else "<event not resolved>"
        return f"{event}: end status '{self.end_status}' with {self.post_processor} post-processor: {super().__str__()}"


class Request(pydantic.BaseModel):
    server_call_name: str
    command_type: ShellCommandActionType
    prompt_state: PromptState
    kwargs: dict = {}

    @staticmethod
    def create_template(
        server_call_id: str, function: ServerCallFunction, command_type: ShellCommandActionType
    ) -> tuple[str, list[str]]:

        parameters = list(inspect.signature(function).parameters.values())[1:]  # excludes prompt_data
        jq_args = []
        placeholders_to_resolve = []
        for parameter in parameters:
            if isinstance(parameter.default, CommandOutput):
                jq_args.append(f'--arg {parameter.name} "$({parameter.default})"')
            else:
                # to be replaced using .resolve or is an environment variable
                jq_args.append(f'--arg {parameter.name} "${parameter.name}"')
                # environmental variables are recognized by being all uppercase
                if not re.match("^[A-Z_]*$", parameter.name):
                    placeholders_to_resolve.append(parameter.name)
        template = (
            PromptState.create_command()
            + " | jq --compact-output '{prompt_state:.} + {"
            + f'server_call_name:"{server_call_id}",command_type:"{command_type}"'
            + "} + {kwargs:$ARGS.named}' "
            + " ".join(jq_args)
            + " | nc localhost $socket_number"
        )
        return template, placeholders_to_resolve


PLACEHOLDERS = {
    "query": "--arg query {q}",  # type str
    "index": "--argjson single_index $(x={n}; echo ${x:-null})",  # type int
    "fzf_selection": f'--argjson single_line "$({SHELL_SCRIPTS.selection_to_json} {{}})"',  # type str
    "indices": f'--argjson indices "$({SHELL_SCRIPTS.indices_to_json} {{+n}})"',  # type list[int]
    "lines": f'--argjson lines "$({SHELL_SCRIPTS.selections_to_json} {{+}})"',  # type list[str]
}


class PromptState(pydantic.BaseModel):
    query: str
    single_index: int | None
    indices: list[int]
    single_line: str | None
    lines: list[str]

    @staticmethod
    def create_command() -> str:
        return f'jq --null-input \'$ARGS.named\' {" ".join(PLACEHOLDERS.values())}'


class Server[T, S](Thread):
    def __init__(
        self,
        prompt_data: PromptData[T, S],
        server_setup_finished: Event,
        server_should_close: Event,
    ) -> None:
        super().__init__(name="Server")
        self.prompt_data = prompt_data
        self.server_setup_finished = server_setup_finished
        self.server_should_close = server_should_close
        self.server_calls: dict[str, ServerCall[T, S]] = {sc.id: sc for sc in prompt_data.server_calls()}

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
                            logger.info("Server closing")
                            break
                        continue
                    logger.info(f"Connection from {addr}")
                    self.handle_request(client_socket, self.prompt_data)
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            self.server_setup_finished.set()

    def handle_request(self, client_socket: socket.socket, prompt_data: PromptData[T, S]):
        payload_bytearray = bytearray()
        while r := client_socket.recv(1024):
            payload_bytearray.extend(r)
        payload = payload_bytearray.decode("utf-8").strip()
        try:
            request = Request.model_validate_json(payload)
            logger.debug(request.server_call_name)
            prompt_data.set_current_state(request.prompt_state)
            function = self.server_calls[request.server_call_name].function
            response = function(prompt_data, **request.kwargs)
        except Exception as err:
            logger.error(trb := traceback.format_exc())
            response = trb
            client_socket.sendall(str(response).encode("utf-8"))
            logger.error(f"Payload contents:\n{payload}")
        else:
            if response:
                client_socket.sendall(str(response).encode("utf-8"))
        finally:
            client_socket.close()

    def resolve_all_server_calls(self, socket_number: int):
        for server_call in self.server_calls.values():
            server_call.resolve_socket_number(socket_number)


type PreviewFunction[T, S] = ServerCallFunctionGeneric[T, S, str]


class Preview[T, S]:
    # TODO: | Event
    # TODO: implement ServerCall commands
    # TODO: line wrap
    def __init__(
        self,
        name: str,
        command: str | PreviewFunction[T, S],
        hotkey: Hotkey | None = None,
        window_size: int | str = "50%",
        window_position: Position = "right",
        preview_label: str | None = None,
        store_output: bool = True,
    ):
        self.name = name
        self.id = f"{name} ({id(self)})"
        self.command = command
        self.hotkey: Hotkey | None = hotkey
        self.window_size = window_size
        self.window_position: Position = window_position
        self.preview_label = preview_label
        self.store_output = store_output
        self._output: str | None = None

    @property
    def output(self) -> str:
        if self._output is None:
            if self.store_output:
                raise RuntimeError("Output not set")
            raise Warning("Output not stored for this preview")
        return self._output

    @output.setter
    def output(self, value: str):
        self._output = value


class PreviewChange[T, S](ServerCall[T, S]):
    def __init__(self, preview: Preview[T, S]) -> None:

        def change_current_preview(prompt_data: PromptData[T, S]):
            prompt_data.previewer.set_current_preview(preview.id)
            logger.trace(f"Changing preview to '{preview.name}'", preview=preview.name)

        super().__init__(change_current_preview, "execute-silent")


class GetCurrentPreviewFromServer(ServerCall):
    def __init__(self, preview: Preview) -> None:
        action_type = "change-preview"
        command = preview.command
        if isinstance(command, str):

            def store_preview_output(
                prompt_data: PromptData, preview_output: str = CommandOutput("echo $preview_output")
            ):
                preview.output = preview_output
                logger.trace(f"Showing preview '{preview.name}'", preview=preview.name)

            super().__init__(store_preview_output, f"Store preview of {preview.name}", action_type)
            self.template = f'preview_output="$({preview.command})"; echo $preview_output && {self.template}'

        else:

            def get_current_preview(prompt_data: PromptData, **kwargs):
                preview.output = command(prompt_data)
                logger.trace(f"Showing preview '{preview.name}'", preview=preview.name)
                return preview.output

            super().__init__(command, f"Show preview of {preview.name}", action_type=action_type)
            # HACK: wanna ServerCall to parse parameters of enclosed function first to create the right template
            self.function = get_current_preview


class PreviewWindowChange(ParametrizedAction):
    def __init__(self, window_size: int | str, window_position: Position) -> None:
        """Window size: int - absolute, str - relative and should be in '<int>%' format"""
        self.window_size = window_size
        self.window_position = window_position
        super().__init__(f"{self.window_size},{self.window_position}", "change-preview-window")


class Previewer[T, S]:
    """Handles storing preview outputs and tracking current preview and possibly other logic associated with previews"""

    def __init__(self) -> None:
        self._previews: dict[str, Preview[T, S]] = {}
        self._current_preview: Preview[T, S] | None = None

    @property
    def current_preview(self) -> Preview[T, S]:
        if not self._current_preview:
            raise RuntimeError("No current preview set")
        return self._current_preview

    def set_current_preview(self, preview_id: str):
        self._current_preview = self.get_preview(preview_id)

    @property
    def previews(self) -> list[Preview[T, S]]:
        return list(self._previews.values())

    def add(self, preview: Preview[T, S], *, main: bool = False):
        if main or not self._previews:
            self._current_preview = preview
        self._previews[preview.id] = preview

    def get_preview(self, preview_id: str) -> Preview[T, S]:
        return self._previews[preview_id]


JSON_ENV_VAR_NAME = "PROMPT_DATA"


class PromptData[T, S]:
    """Accessed from fzf process through socket Server"""

    def __init__(
        self,
        choices: list[T] | None = None,
        presented_choices: list[str] | None = None,
        obj: S = None,
        data: dict | None = None,  # arbitrary data to be passed to fzf process
        previewer: Previewer[T, S] | None = None,
        action_menu: ActionMenu[T, S] | None = None,
        options: Options | None = None,
        data_as_env_var: bool = False,
    ):
        self.choices = choices or []
        self.presented_choices = presented_choices or [str(choice) for choice in self.choices]
        self.obj = obj
        self.data = data or {}
        self.previewer = previewer or Previewer()
        self.action_menu = action_menu or ActionMenu(self.previewer)
        self.options = options or Options()
        self.data_as_env_var = data_as_env_var
        self.post_processors: list[PostProcessor] = []
        self._current_state: PromptState | None = None
        self._result: Result[T]
        self.id = datetime.now().isoformat()  # TODO: Use it?
        self._finished = False

    @property
    def current_state(self) -> PromptState:
        if not self._current_state:
            raise RuntimeError("Current state not set")
        return self._current_state

    def set_current_state(self, prompt_state: PromptState):
        self._current_state = prompt_state

    @property
    def result(self) -> Result[T]:
        try:
            return self._result
        except AttributeError as err:
            raise RuntimeError("Result not set") from err

    @property
    def finished(self) -> bool:
        return self._finished

    def finish(self, event: Hotkey | Situation, end_status: EndStatus):
        self._result = Result(
            end_status=end_status,
            event=event,
            choices=self.choices,
            query=self.current_state.query,
            single_index=self.current_state.single_index,
            indices=self.current_state.indices,
            single_line=self.current_state.single_line,
            lines=self.current_state.lines,
        )
        self._finished = True

    @property
    def choices_string(self) -> str:
        return "\n".join(self.presented_choices)

    def get_current_preview(self) -> str:
        return self.action_menu.previewer.current_preview.output

    def add_preview(
        self, preview: Preview, *, conflict_resolution: ConflictResolution = "raise error", main: bool = False
    ):
        if preview.hotkey:
            self.action_menu.add(
                preview.hotkey,
                # ❗ It's crucial that window change happens before preview change
                Binding(
                    f"Change preview to '{preview.name}'",
                    PreviewWindowChange(preview.window_size, preview.window_position),
                    PreviewChange(preview),
                    (
                        ShellCommand(preview.command, "change-preview")
                        if not preview.store_output and isinstance(preview.command, str)
                        else GetCurrentPreviewFromServer(preview)
                    ),
                ),
                conflict_resolution=conflict_resolution,
            )
        self.previewer.add(preview, main=main)

    def add_post_processor(self, post_processor: PostProcessor):
        self.post_processors.append(post_processor)

    def apply_common_post_processors(self, prompt_data: PromptData[T, S]):
        for post_processor in self.post_processors:
            post_processor(prompt_data)

    @single_use_method
    def resolve_options(self) -> Options:
        return self.options + self.action_menu.resolve_options()

    def server_calls(self) -> list[ServerCall]:
        server_calls = [action for action in self.action_menu.actions if isinstance(action, ServerCall)]
        if self.action_menu.should_run_automator:
            return [*server_calls, self.action_menu.automator.move_to_next_binding_server_call]
        return server_calls
