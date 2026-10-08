from __future__ import annotations

from typing import Any, Callable


# TODO: Add it to utils
class classproperty[T]:
    def __init__(self, fget: Callable[[Any], T]):
        self.fget = fget
        self.__doc__ = fget.__doc__

    # HACK: ❗ Type-checker doesn't know you're passing class into the method but you don't use the parameter anyway
    def __get__(self, obj, cls) -> T:
        return self.fget(cls)


class CommandOutput(str):
    """
    A special type of value that when used as default value in ServerCallFunction parameters
    will be executed as a shell command and the output will be passed as str to the parameter.
    """


class VarOutput(str):
    """A special type of value that when used as default value in ServerCallFunction parameters
    will be read from a shell variable and the value will be passed as str to the parameter.

    preset: Pick preset fzf environment variable
    """

    @classproperty
    def preset(_) -> FzfEnvVarPicker:
        """Pick preset fzf environment variable"""
        return FzfEnvVarPicker()


class FzfEnvVarPicker:
    @property
    def FZF_LINES(_):
        """Number of lines fzf takes up excluding padding and margin"""
        return VarOutput("FZF_LINES")

    @property
    def FZF_COLUMNS(_):
        """Number of columns fzf takes up excluding padding and margin"""
        return VarOutput("FZF_COLUMNS")

    @property
    def FZF_DIRECTION(_):
        """Direction of the list (up or down)"""
        return VarOutput("FZF_DIRECTION")

    @property
    def FZF_TOTAL_COUNT(_):
        """Total number of items"""
        return VarOutput("FZF_TOTAL_COUNT")

    @property
    def FZF_MATCH_COUNT(_):
        """Number of matched items"""
        return VarOutput("FZF_MATCH_COUNT")

    @property
    def FZF_SELECT_COUNT(_):
        """Number of selected items"""
        return VarOutput("FZF_SELECT_COUNT")

    @property
    def FZF_POS(_):
        """Vertical position of the cursor in the list starting from 1"""
        return VarOutput("FZF_POS")

    @property
    def FZF_CURRENT_ITEM(_):
        """Text of the current item (unset if the list is empty)
        is omitted when the item contains a NUL byte, because exec(2) cannot pass it.
        It is also omitted when the item is larger than 64 KB, so that a huge item cannot overflow
        the environment size limit and break preview and other child commands.
        """
        return VarOutput("FZF_CURRENT_ITEM")

    @property
    def FZF_WRAP(_):
        """The line wrapping mode (char, word) when enabled"""
        return VarOutput("FZF_WRAP")

    @property
    def FZF_QUERY(_):
        """Current query string"""
        return VarOutput("FZF_QUERY")

    @property
    def FZF_INPUT_STATE(_):
        """Current input state (enabled, disabled, hidden)"""
        return VarOutput("FZF_INPUT_STATE")

    @property
    def FZF_NTH(_):
        """Current --nth option"""
        return VarOutput("FZF_NTH")

    @property
    def FZF_WITH_NTH(_):
        """Current --with-nth option"""
        return VarOutput("FZF_WITH_NTH")

    @property
    def FZF_PROMPT(_):
        """Prompt string"""
        return VarOutput("FZF_PROMPT")

    @property
    def FZF_GHOST(_):
        """Ghost string"""
        return VarOutput("FZF_GHOST")

    @property
    def FZF_POINTER(_):
        """Pointer string"""
        return VarOutput("FZF_POINTER")

    @property
    def FZF_PREVIEW_LABEL(_):
        """Preview label string"""
        return VarOutput("FZF_PREVIEW_LABEL")

    @property
    def FZF_BORDER_LABEL(_):
        """Border label string"""
        return VarOutput("FZF_BORDER_LABEL")

    @property
    def FZF_LIST_LABEL(_):
        """List label string"""
        return VarOutput("FZF_LIST_LABEL")

    @property
    def FZF_INPUT_LABEL(_):
        """Input label string"""
        return VarOutput("FZF_INPUT_LABEL")

    @property
    def FZF_HEADER_LABEL(_):
        """Header label string"""
        return VarOutput("FZF_HEADER_LABEL")

    @property
    def FZF_ACTION(_):
        """The name of the last action performed"""
        return VarOutput("FZF_ACTION")

    @property
    def FZF_KEY(_):
        """The name of the last key pressed"""
        return VarOutput("FZF_KEY")

    @property
    def FZF_IDLE_TIME(_):
        """Whole seconds since the last user activity"""
        return VarOutput("FZF_IDLE_TIME")

    @property
    def FZF_IDLE_TIME_MS(_):
        """Milliseconds since the last user activity"""
        return VarOutput("FZF_IDLE_TIME_MS")

    @property
    def FZF_PORT(_):
        """Port number when --listen option is used"""
        return VarOutput("FZF_PORT")

    @property
    def FZF_SOCK(_):
        """Unix socket path when --listen option is used"""
        return VarOutput("FZF_SOCK")

    @property
    def FZF_PREVIEW_TOP(_):
        """Top position of the preview window"""
        return VarOutput("FZF_PREVIEW_TOP")

    @property
    def FZF_PREVIEW_LEFT(_):
        """Left position of the preview window"""
        return VarOutput("FZF_PREVIEW_LEFT")

    @property
    def FZF_PREVIEW_LINES(_):
        """Number of lines in the preview window"""
        return VarOutput("FZF_PREVIEW_LINES")

    @property
    def FZF_PREVIEW_COLUMNS(_):
        """Number of columns in the preview window"""
        return VarOutput("FZF_PREVIEW_COLUMNS")

    @property
    def FZF_RAW(_):
        """Only in raw mode. 1 if the current item matches, 0 otherwise"""
        return VarOutput("FZF_RAW")


class FzfPlaceholder(str):
    """
    A special type of value if used as default ServerCallFunction parameter
    will be evaluated as a fzf placeholder and passed as str to the parameter.

    preset: Pick preset FzfPlaceholder
    """

    @classproperty
    def preset(_) -> FzfPlaceholderPicker:
        """Pick preset fzf placeholder"""
        return FzfPlaceholderPicker()


class FzfPlaceholderPicker:
    @property
    def QUERY(_):
        """Current query string"""
        return FzfPlaceholder("{q}")

    @property
    def CURRENT_ITEM(_):
        """Single-quoted string of the current item"""
        return FzfPlaceholder("{}")

    @property
    def CURRENT_INDEX(_):
        """0-based index of the current item"""
        return FzfPlaceholder("{n}")

    @property
    def TARGET_ITEMS(_):
        """Space-separated list of the selected items (or the current item if no selection was made) individually quoted"""
        return FzfPlaceholder('"{+}"')

    @property
    def TARGET_INDICES(_):
        """Space-separated list of the 0-based indices of the selected items (or the current item if no selection was made)"""
        return FzfPlaceholder('"{+n}"')

    @property
    def TARGET_ITEMS_FILE(_):
        """File with newline-separated list of the selected items (or the current item if no selection was made)"""
        return FzfPlaceholder("{+f}")

    @property
    def TARGET_INDICES_FILE(_):
        """File with newline-separated list of the 0-based indices of the selected items (or the current item if no selection was made)"""
        return FzfPlaceholder("{+nf}")

    @property
    def MATCHED_ITEMS(_):
        """Space-separated list of the matched items individually quoted"""
        return FzfPlaceholder('"{*}"')

    @property
    def MATCHED_INDICES(_):
        """Space-separated list of the 0-based indices of the matched items"""
        return FzfPlaceholder('"{*n}"')

    @property
    def MATCHED_ITEMS_FILE(_):
        """File with newline-separated list of the matched items"""
        return FzfPlaceholder("{*f}")

    @property
    def MATCHED_INDICES_FILE(_):
        """File with newline-separated list of the 0-based indices of the matched items"""
        return FzfPlaceholder("{*nf}")
