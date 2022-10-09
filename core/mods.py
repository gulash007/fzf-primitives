from core.exceptions import ExitLoop, ExitRound
from thingies import decorator
import clipboard


@decorator
def exit_on_no_selection(func, self, options, *args, **kwargs):
    if output := func(self, options, *args, **kwargs):
        return output
    raise ExitRound


@decorator
def ansi(func, self, options, *args, **kwargs):
    return func(self, f"{options} --ansi", *args, **kwargs)


@decorator
def multiselect(func, self, options, *args, **kwargs):
    return func(self, f"{options} --multi", *args, **kwargs)


@decorator
def clip_output(func, self, options, *args, **kwargs):
    output = func(self, options, *args, **kwargs)
    clipboard.copy("\n".join(output) if isinstance(output, list) else output)
    return output
