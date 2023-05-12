# Syntax sugar layer

import functools
from typing import Any, Callable, Generic, ParamSpec, Protocol

import clipboard

from .exceptions import ExitLoop, ExitRound
from .FzfPrompt.ActionMenu import Action
from .FzfPrompt.commands import ACTION, SHELL_COMMAND
from .FzfPrompt.decorators import constructor
from .FzfPrompt.options import Hotkey, Options
from .FzfPrompt.Previewer import Preview
from .FzfPrompt.Prompt import Result
from .FzfPrompt.PromptData import PromptData
from .monitoring.Logger import get_logger

P = ParamSpec("P")
logger = get_logger()


class Moddable(Protocol, Generic[P]):
    @staticmethod
    def __call__(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs) -> Result:
        ...


def add_options(added_options: Options):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def adding_options(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options = prompt_data.options + added_options
            return func(prompt_data, *args, **kwargs)

        return adding_options

    return decorator


multiselect = add_options(Options().multiselect)
ansi = add_options(Options().ansi)
no_sort = add_options(Options().no_sort)


def exit_round_on_no_selection(message: str = ""):
    def decorator(func: Moddable[P]) -> Moddable[P]:
        def exiting_round_on_no_selection(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            if not (result := func(prompt_data, *args, **kwargs)) and not result.hotkey:
                logger.info(message)
                raise ExitRound(message)
            return result

        return exiting_round_on_no_selection

    return decorator


# TODO: make it somehow compatible with multi or throw it away
# TODO: decorator factory type hinting
# TODO: preview label


get_preview = constructor(Preview)


class preview:
    basic = functools.partial(get_preview, "basic", None)
    custom = staticmethod(get_preview)  # without staticmethod decorator get_preview is treated like instance method

    @staticmethod
    def file(language: str = "python", theme: str = "Solarized (light)"):
        language_arg = f"--language {language}" if language else ""
        theme_arg = f'--theme "{theme}"' if theme else ""
        return functools.partial(
            get_preview,
            "View File",
            f"python3.11 -m fzf_primitives.core.actions.view_file {{q}} {{+}} {language_arg} {theme_arg}",
        )


def action_python(result_processor: Callable[[Result], Any], hk: Hotkey):
    def deco(func: Moddable[P]) -> Moddable[P]:
        def with_python_hotkey(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
            prompt_data.options.expect(hk)
            prompt_data.action_menu.add(Action(result_processor.__name__, "accept", hk))
            result = func(prompt_data, *args, **kwargs)
            return result_processor(result) if result.hotkey == hk else result

        return with_python_hotkey

    return deco


def quit_app(result: Result):
    sep = "\n\t"
    raise ExitLoop(f"Exiting app with\nquery: {result.query}\nselections:{sep}{sep.join(result)}")


get_action = constructor(Action)


class action:
    clip = functools.partial(get_action, "clip selections", ACTION.execute_silent(SHELL_COMMAND.clip_selections))
    select_all = functools.partial(get_action, "select all", ACTION.select_all)
    toggle_all = functools.partial(get_action, "toggle all", ACTION.toggle_all)
    custom = staticmethod(get_action)
    quit = functools.partial(action_python, quit_app)


def clip_output(func: Moddable[P]) -> Moddable[P]:
    def clipping_output(prompt_data: PromptData, *args: P.args, **kwargs: P.kwargs):
        result = func(prompt_data, *args, **kwargs)
        clipboard.copy("\n".join(result))
        return result

    return clipping_output
