from typing import Callable

from core.options import Options
from pyfzf import FzfPrompt


class Hotkeys:
    def __init__(self, hotkey_actions) -> None:
        self._hotkey_actions = hotkey_actions

    def __call__(self, obj: Callable):
        def with_hotkeys(slf, options: Options = Options(), *args, **kwargs):
            hotkey, output = obj(slf, options.expect(*self._hotkey_actions.keys()), *args, **kwargs)
            print(hotkey)
            action = self._hotkey_actions.get(hotkey)
            if action:
                action(slf)
            return output

        return with_hotkeys


if __name__ == "__main__":
    import functools

    hotkeys = Hotkeys(
        {
            key: functools.partial(lambda slf, key: print(f"{slf}: Pressing {key}"), key=key)
            for key in ("ctrl-q", "enter", "ctrl-a")
        }
    )
    print(hotkeys._hotkey_actions)

    class X:
        @hotkeys
        def pr(self, options: Options = Options()):
            choices = [1, 2, 3]
            return FzfPrompt().prompt(choices=choices, fzf_options=str(options))

    x = X()
    print(x.pr())
