from typing import TYPE_CHECKING, Callable

from ..FzfPrompt.options import Hotkey, Situation
from .on_event import OnEvent

if TYPE_CHECKING:
    from .preview_mod import PreviewMutationOnEvent


class SituationAdder[M: (OnEvent, PreviewMutationOnEvent)]:
    def __init__(self, mod_adder: Callable[[Situation], M]):
        self._mod_adder = mod_adder

    def _set_and_return_mod(self, situation: Situation) -> M:
        return self._mod_adder(situation)

    @property
    def START(self) -> M:
        """Triggered only once when fzf finder starts. Since fzf consumes the input stream asynchronously, the input list is not available unless you use --sync"""
        return self._set_and_return_mod("start")

    @property
    def LOAD(self) -> M:
        """Triggered when the input stream is complete and the initial processing of the list is complete"""
        return self._set_and_return_mod("load")

    @property
    def RESIZE(self) -> M:
        """Triggered when the terminal size is changed"""
        return self._set_and_return_mod("resize")

    @property
    def RESULT(self) -> M:
        """Triggered when the filtering for the current query is complete and the result list is ready"""
        return self._set_and_return_mod("result")

    @property
    def CHANGE(self) -> M:
        """Triggered whenever the query string is changed"""
        return self._set_and_return_mod("change")

    @property
    def FOCUS(self) -> M:
        """Triggered when the focus changes due to a vertical cursor movement or a search result update"""
        return self._set_and_return_mod("focus")

    @property
    def ONE(self) -> M:
        """Triggered when there's only one match"""
        return self._set_and_return_mod("one")

    @property
    def ZERO(self) -> M:
        """Triggered when there's no match"""
        return self._set_and_return_mod("zero")

    @property
    def BACKWARD_EOF(self) -> M:
        """Triggered when the query string is already empty and you try to delete it backward"""
        return self._set_and_return_mod("backward-eof")

    @property
    def JUMP(self) -> M:
        """Triggered when successfully jumped to the target item in jump mode"""
        return self._set_and_return_mod("backward-eof")

    @property
    def JUMP_CANCEL(self) -> M:
        """Triggered when jump mode is cancelled"""
        return self._set_and_return_mod("backward-eof")


class HotkeyAdder[M: (OnEvent, PreviewMutationOnEvent)]:
    def __init__(self, mod_adder: Callable[[Hotkey], M]):
        self._mod_adder = mod_adder

    def _set_and_return_mod(self, hotkey: Hotkey) -> M:
        return self._mod_adder(hotkey)

    @property
    def ALT_0(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-0")

    @property
    def ALT_1(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-1")

    @property
    def ALT_2(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-2")

    @property
    def ALT_3(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-3")

    @property
    def ALT_4(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-4")

    @property
    def ALT_5(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-5")

    @property
    def ALT_6(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-6")

    @property
    def ALT_7(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-7")

    @property
    def ALT_8(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-8")

    @property
    def ALT_9(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-9")

    @property
    def ALT_A(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-a")

    @property
    def ALT_B(self) -> M:
        """Default: backward-word"""
        return self._set_and_return_mod("alt-b")

    @property
    def ALT_BS(self) -> M:
        """Default: backward-kill-word"""
        return self._set_and_return_mod("alt-bs")

    @property
    def ALT_C(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-c")

    @property
    def ALT_D(self) -> M:
        """Default: kill-word"""
        return self._set_and_return_mod("alt-d")

    @property
    def ALT_DOWN(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-down")

    @property
    def ALT_E(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-e")

    @property
    def ALT_F(self) -> M:
        """Default: forward-word"""
        return self._set_and_return_mod("alt-f")

    @property
    def ALT_G(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-g")

    @property
    def ALT_H(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-h")

    @property
    def ALT_I(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-i")

    @property
    def ALT_J(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-j")

    @property
    def ALT_K(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-k")

    @property
    def ALT_L(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-l")

    @property
    def ALT_M(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-m")

    @property
    def ALT_N(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-n")

    @property
    def ALT_O(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-o")

    @property
    def ALT_P(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-p")

    @property
    def ALT_Q(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-q")

    @property
    def ALT_R(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-r")

    @property
    def ALT_S(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-s")

    @property
    def ALT_T(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-t")

    @property
    def ALT_U(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-u")

    @property
    def ALT_UP(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-up")

    @property
    def ALT_V(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-v")

    @property
    def ALT_W(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-w")

    @property
    def ALT_X(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-x")

    @property
    def ALT_Y(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-y")

    @property
    def ALT_Z(self) -> M:
        """Free"""
        return self._set_and_return_mod("alt-z")

    @property
    def BSPACE(self) -> M:
        """Default: backward-delete-char"""
        return self._set_and_return_mod("bspace")

    @property
    def CTRL_6(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-6")

    @property
    def CTRL_A(self) -> M:
        """Default: beginning-of-line"""
        return self._set_and_return_mod("ctrl-a")

    @property
    def CTRL_ALT_A(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-a")

    @property
    def CTRL_ALT_B(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-b")

    @property
    def CTRL_ALT_C(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-c")

    @property
    def CTRL_ALT_D(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-d")

    @property
    def CTRL_ALT_E(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-e")

    @property
    def CTRL_ALT_F(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-f")

    @property
    def CTRL_ALT_G(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-g")

    @property
    def CTRL_ALT_H(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-h")

    @property
    def CTRL_ALT_I(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-i")

    @property
    def CTRL_ALT_J(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-j")

    @property
    def CTRL_ALT_K(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-k")

    @property
    def CTRL_ALT_L(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-l")

    @property
    def CTRL_ALT_M(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-m")

    @property
    def CTRL_ALT_N(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-n")

    @property
    def CTRL_ALT_O(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-o")

    @property
    def CTRL_ALT_P(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-p")

    @property
    def CTRL_ALT_Q(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-q")

    @property
    def CTRL_ALT_R(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-r")

    @property
    def CTRL_ALT_S(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-s")

    @property
    def CTRL_ALT_T(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-t")

    @property
    def CTRL_ALT_U(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-u")

    @property
    def CTRL_ALT_V(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-v")

    @property
    def CTRL_ALT_W(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-w")

    @property
    def CTRL_ALT_X(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-x")

    @property
    def CTRL_ALT_Y(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-y")

    @property
    def CTRL_ALT_Z(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-alt-z")

    @property
    def CTRL_B(self) -> M:
        """Default: backward-char"""
        return self._set_and_return_mod("ctrl-b")

    @property
    def CTRL_C(self) -> M:
        """Default: abort"""
        return self._set_and_return_mod("ctrl-c")

    @property
    def CTRL_D(self) -> M:
        """Default: delete-char/eof"""
        return self._set_and_return_mod("ctrl-d")

    @property
    def CTRL_E(self) -> M:
        """Default: end-of-line"""
        return self._set_and_return_mod("ctrl-e")

    @property
    def CTRL_F(self) -> M:
        """Default: forward-char"""
        return self._set_and_return_mod("ctrl-f")

    @property
    def CTRL_G(self) -> M:
        """Default: abort"""
        return self._set_and_return_mod("ctrl-g")

    @property
    def CTRL_H(self) -> M:
        """Default: backward-delete-char"""
        return self._set_and_return_mod("ctrl-h")

    @property
    def CTRL_I(self) -> M:
        """Default: toggle+down"""
        return self._set_and_return_mod("ctrl-i")

    @property
    def CTRL_J(self) -> M:
        """Default: down"""
        return self._set_and_return_mod("ctrl-j")

    @property
    def CTRL_K(self) -> M:
        """Default: up"""
        return self._set_and_return_mod("ctrl-k")

    @property
    def CTRL_L(self) -> M:
        """Default: clear-screen"""
        return self._set_and_return_mod("ctrl-l")

    @property
    def CTRL_N(self) -> M:
        """Default: down"""
        return self._set_and_return_mod("ctrl-n")

    @property
    def CTRL_O(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-o")

    @property
    def CTRL_P(self) -> M:
        """Default: up"""
        return self._set_and_return_mod("ctrl-p")

    @property
    def CTRL_Q(self) -> M:
        """Default: abort"""
        return self._set_and_return_mod("ctrl-q")

    @property
    def CTRL_R(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-r")

    @property
    def CTRL_S(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-s")

    @property
    def CTRL_T(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-t")

    @property
    def CTRL_U(self) -> M:
        """Default: unix-line-discard"""
        return self._set_and_return_mod("ctrl-u")

    @property
    def CTRL_V(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-v")

    @property
    def CTRL_W(self) -> M:
        """Default: unix-word-rubout"""
        return self._set_and_return_mod("ctrl-w")

    @property
    def CTRL_X(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-x")

    @property
    def CTRL_Y(self) -> M:
        """Default: yank"""
        return self._set_and_return_mod("ctrl-y")

    @property
    def CTRL_Z(self) -> M:
        """Free"""
        return self._set_and_return_mod("ctrl-z")

    @property
    def DEL(self) -> M:
        """Default: delete-char"""
        return self._set_and_return_mod("del")

    @property
    def DOUBLE_CLICK(self) -> M:
        """Default: accept"""
        return self._set_and_return_mod("double-click")

    @property
    def DOWN(self) -> M:
        """Default: down"""
        return self._set_and_return_mod("down")

    @property
    def END(self) -> M:
        """Default: end-of-line"""
        return self._set_and_return_mod("end")

    @property
    def ENTER(self) -> M:
        """Default: accept"""
        return self._set_and_return_mod("enter")

    @property
    def ESC(self) -> M:
        """Default: abort"""
        return self._set_and_return_mod("esc")

    @property
    def F1(self) -> M:
        """Free"""
        return self._set_and_return_mod("f1")

    @property
    def F2(self) -> M:
        """Free"""
        return self._set_and_return_mod("f2")

    @property
    def F3(self) -> M:
        """Free"""
        return self._set_and_return_mod("f3")

    @property
    def F4(self) -> M:
        """Free"""
        return self._set_and_return_mod("f4")

    @property
    def F5(self) -> M:
        """Free"""
        return self._set_and_return_mod("f5")

    @property
    def F6(self) -> M:
        """Free"""
        return self._set_and_return_mod("f6")

    @property
    def F7(self) -> M:
        """Free"""
        return self._set_and_return_mod("f7")

    @property
    def F8(self) -> M:
        """Free"""
        return self._set_and_return_mod("f8")

    @property
    def F9(self) -> M:
        """Free"""
        return self._set_and_return_mod("f9")

    @property
    def F10(self) -> M:
        """Free"""
        return self._set_and_return_mod("f10")

    @property
    def F11(self) -> M:
        """Free"""
        return self._set_and_return_mod("f11")

    @property
    def F12(self) -> M:
        """Free"""
        return self._set_and_return_mod("f12")

    @property
    def HOME(self) -> M:
        """Default: beginning-of-line"""
        return self._set_and_return_mod("home")

    @property
    def LEFT(self) -> M:
        """Default: backward-char"""
        return self._set_and_return_mod("left")

    @property
    def PGDN(self) -> M:
        """Default: page-down"""
        return self._set_and_return_mod("pgdn")

    @property
    def PGUP(self) -> M:
        """Default: page-up"""
        return self._set_and_return_mod("pgup")

    @property
    def RIGHT(self) -> M:
        """Default: forward-char"""
        return self._set_and_return_mod("right")

    @property
    def RIGHT_CLICK(self) -> M:
        """Default: toggle"""
        return self._set_and_return_mod("right-click")

    @property
    def SHIFT_DOWN(self) -> M:
        """Default: preview-down"""
        return self._set_and_return_mod("shift-down")

    @property
    def SHIFT_LEFT(self) -> M:
        """Default: backward-word"""
        return self._set_and_return_mod("shift-left")

    @property
    def SHIFT_RIGHT(self) -> M:
        """Default: forward-word"""
        return self._set_and_return_mod("shift-right")

    @property
    def SHIFT_TAB(self) -> M:
        """Default: toggle+up"""
        return self._set_and_return_mod("shift-tab")

    @property
    def SHIFT_UP(self) -> M:
        """Default: preview-up"""
        return self._set_and_return_mod("shift-up")

    @property
    def TAB(self) -> M:
        """Default: toggle+down"""
        return self._set_and_return_mod("tab")

    @property
    def UP(self) -> M:
        """Default: up"""
        return self._set_and_return_mod("up")
