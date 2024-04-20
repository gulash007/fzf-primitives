from .on_event import OnEvent


class SituationAdder[M: OnEvent]:
    def __init__(self, mod: M):
        self._mod = mod

    @property
    def START(self) -> M:
        """Triggered only once when fzf finder starts. Since fzf consumes the input stream asynchronously, the input list is not available unless you use --sync"""
        self._mod.set_event("start")
        return self._mod

    @property
    def LOAD(self) -> M:
        """Triggered when the input stream is complete and the initial processing of the list is complete"""
        self._mod.set_event("load")
        return self._mod

    @property
    def RESIZE(self) -> M:
        """Triggered when the terminal size is changed"""
        self._mod.set_event("resize")
        return self._mod

    @property
    def RESULT(self) -> M:
        """Triggered when the filtering for the current query is complete and the result list is ready"""
        self._mod.set_event("result")
        return self._mod

    @property
    def CHANGE(self) -> M:
        """Triggered whenever the query string is changed"""
        self._mod.set_event("change")
        return self._mod

    @property
    def FOCUS(self) -> M:
        """Triggered when the focus changes due to a vertical cursor movement or a search result update"""
        self._mod.set_event("focus")
        return self._mod

    @property
    def ONE(self) -> M:
        """Triggered when there's only one match"""
        self._mod.set_event("one")
        return self._mod

    @property
    def ZERO(self) -> M:
        """Triggered when there's no match"""
        self._mod.set_event("zero")
        return self._mod

    @property
    def BACKWARD_EOF(self) -> M:
        """Triggered when the query string is already empty and you try to delete it backward"""
        self._mod.set_event("backward-eof")
        return self._mod


class HotkeyAdder[M: OnEvent]:
    def __init__(self, mod: M):
        self._mod = mod

    @property
    def ALT_0(self) -> M:
        """Free"""
        self._mod.set_event("alt-0")
        return self._mod

    @property
    def ALT_1(self) -> M:
        """Free"""
        self._mod.set_event("alt-1")
        return self._mod

    @property
    def ALT_2(self) -> M:
        """Free"""
        self._mod.set_event("alt-2")
        return self._mod

    @property
    def ALT_3(self) -> M:
        """Free"""
        self._mod.set_event("alt-3")
        return self._mod

    @property
    def ALT_4(self) -> M:
        """Free"""
        self._mod.set_event("alt-4")
        return self._mod

    @property
    def ALT_5(self) -> M:
        """Free"""
        self._mod.set_event("alt-5")
        return self._mod

    @property
    def ALT_6(self) -> M:
        """Free"""
        self._mod.set_event("alt-6")
        return self._mod

    @property
    def ALT_7(self) -> M:
        """Free"""
        self._mod.set_event("alt-7")
        return self._mod

    @property
    def ALT_8(self) -> M:
        """Free"""
        self._mod.set_event("alt-8")
        return self._mod

    @property
    def ALT_9(self) -> M:
        """Free"""
        self._mod.set_event("alt-9")
        return self._mod

    @property
    def ALT_A(self) -> M:
        """Free"""
        self._mod.set_event("alt-a")
        return self._mod

    @property
    def ALT_B(self) -> M:
        """Default: backward-word"""
        self._mod.set_event("alt-b")
        return self._mod

    @property
    def ALT_BS(self) -> M:
        """Default: backward-kill-word"""
        self._mod.set_event("alt-bs")
        return self._mod

    @property
    def ALT_C(self) -> M:
        """Free"""
        self._mod.set_event("alt-c")
        return self._mod

    @property
    def ALT_D(self) -> M:
        """Default: kill-word"""
        self._mod.set_event("alt-d")
        return self._mod

    @property
    def ALT_DOWN(self) -> M:
        """Free"""
        self._mod.set_event("alt-down")
        return self._mod

    @property
    def ALT_E(self) -> M:
        """Free"""
        self._mod.set_event("alt-e")
        return self._mod

    @property
    def ALT_F(self) -> M:
        """Default: forward-word"""
        self._mod.set_event("alt-f")
        return self._mod

    @property
    def ALT_G(self) -> M:
        """Free"""
        self._mod.set_event("alt-g")
        return self._mod

    @property
    def ALT_H(self) -> M:
        """Free"""
        self._mod.set_event("alt-h")
        return self._mod

    @property
    def ALT_I(self) -> M:
        """Free"""
        self._mod.set_event("alt-i")
        return self._mod

    @property
    def ALT_J(self) -> M:
        """Free"""
        self._mod.set_event("alt-j")
        return self._mod

    @property
    def ALT_K(self) -> M:
        """Free"""
        self._mod.set_event("alt-k")
        return self._mod

    @property
    def ALT_L(self) -> M:
        """Free"""
        self._mod.set_event("alt-l")
        return self._mod

    @property
    def ALT_M(self) -> M:
        """Free"""
        self._mod.set_event("alt-m")
        return self._mod

    @property
    def ALT_N(self) -> M:
        """Free"""
        self._mod.set_event("alt-n")
        return self._mod

    @property
    def ALT_O(self) -> M:
        """Free"""
        self._mod.set_event("alt-o")
        return self._mod

    @property
    def ALT_P(self) -> M:
        """Free"""
        self._mod.set_event("alt-p")
        return self._mod

    @property
    def ALT_Q(self) -> M:
        """Free"""
        self._mod.set_event("alt-q")
        return self._mod

    @property
    def ALT_R(self) -> M:
        """Free"""
        self._mod.set_event("alt-r")
        return self._mod

    @property
    def ALT_S(self) -> M:
        """Free"""
        self._mod.set_event("alt-s")
        return self._mod

    @property
    def ALT_T(self) -> M:
        """Free"""
        self._mod.set_event("alt-t")
        return self._mod

    @property
    def ALT_U(self) -> M:
        """Free"""
        self._mod.set_event("alt-u")
        return self._mod

    @property
    def ALT_UP(self) -> M:
        """Free"""
        self._mod.set_event("alt-up")
        return self._mod

    @property
    def ALT_V(self) -> M:
        """Free"""
        self._mod.set_event("alt-v")
        return self._mod

    @property
    def ALT_W(self) -> M:
        """Free"""
        self._mod.set_event("alt-w")
        return self._mod

    @property
    def ALT_X(self) -> M:
        """Free"""
        self._mod.set_event("alt-x")
        return self._mod

    @property
    def ALT_Y(self) -> M:
        """Free"""
        self._mod.set_event("alt-y")
        return self._mod

    @property
    def ALT_Z(self) -> M:
        """Free"""
        self._mod.set_event("alt-z")
        return self._mod

    @property
    def BSPACE(self) -> M:
        """Default: backward-delete-char"""
        self._mod.set_event("bspace")
        return self._mod

    @property
    def CTRL_6(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-6")
        return self._mod

    @property
    def CTRL_A(self) -> M:
        """Default: beginning-of-line"""
        self._mod.set_event("ctrl-a")
        return self._mod

    @property
    def CTRL_ALT_A(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-a")
        return self._mod

    @property
    def CTRL_ALT_B(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-b")
        return self._mod

    @property
    def CTRL_ALT_C(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-c")
        return self._mod

    @property
    def CTRL_ALT_D(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-d")
        return self._mod

    @property
    def CTRL_ALT_E(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-e")
        return self._mod

    @property
    def CTRL_ALT_F(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-f")
        return self._mod

    @property
    def CTRL_ALT_G(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-g")
        return self._mod

    @property
    def CTRL_ALT_H(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-h")
        return self._mod

    @property
    def CTRL_ALT_I(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-i")
        return self._mod

    @property
    def CTRL_ALT_J(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-j")
        return self._mod

    @property
    def CTRL_ALT_K(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-k")
        return self._mod

    @property
    def CTRL_ALT_L(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-l")
        return self._mod

    @property
    def CTRL_ALT_M(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-m")
        return self._mod

    @property
    def CTRL_ALT_N(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-n")
        return self._mod

    @property
    def CTRL_ALT_O(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-o")
        return self._mod

    @property
    def CTRL_ALT_P(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-p")
        return self._mod

    @property
    def CTRL_ALT_Q(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-q")
        return self._mod

    @property
    def CTRL_ALT_R(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-r")
        return self._mod

    @property
    def CTRL_ALT_S(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-s")
        return self._mod

    @property
    def CTRL_ALT_T(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-t")
        return self._mod

    @property
    def CTRL_ALT_U(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-u")
        return self._mod

    @property
    def CTRL_ALT_V(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-v")
        return self._mod

    @property
    def CTRL_ALT_W(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-w")
        return self._mod

    @property
    def CTRL_ALT_X(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-x")
        return self._mod

    @property
    def CTRL_ALT_Y(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-y")
        return self._mod

    @property
    def CTRL_ALT_Z(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-alt-z")
        return self._mod

    @property
    def CTRL_B(self) -> M:
        """Default: backward-char"""
        self._mod.set_event("ctrl-b")
        return self._mod

    @property
    def CTRL_C(self) -> M:
        """Default: abort"""
        self._mod.set_event("ctrl-c")
        return self._mod

    @property
    def CTRL_D(self) -> M:
        """Default: delete-char/eof"""
        self._mod.set_event("ctrl-d")
        return self._mod

    @property
    def CTRL_E(self) -> M:
        """Default: end-of-line"""
        self._mod.set_event("ctrl-e")
        return self._mod

    @property
    def CTRL_F(self) -> M:
        """Default: forward-char"""
        self._mod.set_event("ctrl-f")
        return self._mod

    @property
    def CTRL_G(self) -> M:
        """Default: abort"""
        self._mod.set_event("ctrl-g")
        return self._mod

    @property
    def CTRL_H(self) -> M:
        """Default: backward-delete-char"""
        self._mod.set_event("ctrl-h")
        return self._mod

    @property
    def CTRL_I(self) -> M:
        """Default: toggle+down"""
        self._mod.set_event("ctrl-i")
        return self._mod

    @property
    def CTRL_J(self) -> M:
        """Default: down"""
        self._mod.set_event("ctrl-j")
        return self._mod

    @property
    def CTRL_K(self) -> M:
        """Default: up"""
        self._mod.set_event("ctrl-k")
        return self._mod

    @property
    def CTRL_L(self) -> M:
        """Default: clear-screen"""
        self._mod.set_event("ctrl-l")
        return self._mod

    @property
    def CTRL_N(self) -> M:
        """Default: down"""
        self._mod.set_event("ctrl-n")
        return self._mod

    @property
    def CTRL_O(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-o")
        return self._mod

    @property
    def CTRL_P(self) -> M:
        """Default: up"""
        self._mod.set_event("ctrl-p")
        return self._mod

    @property
    def CTRL_Q(self) -> M:
        """Default: abort"""
        self._mod.set_event("ctrl-q")
        return self._mod

    @property
    def CTRL_R(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-r")
        return self._mod

    @property
    def CTRL_S(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-s")
        return self._mod

    @property
    def CTRL_T(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-t")
        return self._mod

    @property
    def CTRL_U(self) -> M:
        """Default: unix-line-discard"""
        self._mod.set_event("ctrl-u")
        return self._mod

    @property
    def CTRL_V(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-v")
        return self._mod

    @property
    def CTRL_W(self) -> M:
        """Default: unix-word-rubout"""
        self._mod.set_event("ctrl-w")
        return self._mod

    @property
    def CTRL_X(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-x")
        return self._mod

    @property
    def CTRL_Y(self) -> M:
        """Default: yank"""
        self._mod.set_event("ctrl-y")
        return self._mod

    @property
    def CTRL_Z(self) -> M:
        """Free"""
        self._mod.set_event("ctrl-z")
        return self._mod

    @property
    def DEL(self) -> M:
        """Default: delete-char"""
        self._mod.set_event("del")
        return self._mod

    @property
    def DOUBLE_CLICK(self) -> M:
        """Default: accept"""
        self._mod.set_event("double-click")
        return self._mod

    @property
    def DOWN(self) -> M:
        """Default: down"""
        self._mod.set_event("down")
        return self._mod

    @property
    def END(self) -> M:
        """Default: end-of-line"""
        self._mod.set_event("end")
        return self._mod

    @property
    def ENTER(self) -> M:
        """Default: accept"""
        self._mod.set_event("enter")
        return self._mod

    @property
    def ESC(self) -> M:
        """Default: abort"""
        self._mod.set_event("esc")
        return self._mod

    @property
    def F1(self) -> M:
        """Free"""
        self._mod.set_event("f1")
        return self._mod

    @property
    def F2(self) -> M:
        """Free"""
        self._mod.set_event("f2")
        return self._mod

    @property
    def F3(self) -> M:
        """Free"""
        self._mod.set_event("f3")
        return self._mod

    @property
    def F4(self) -> M:
        """Free"""
        self._mod.set_event("f4")
        return self._mod

    @property
    def F5(self) -> M:
        """Free"""
        self._mod.set_event("f5")
        return self._mod

    @property
    def F6(self) -> M:
        """Free"""
        self._mod.set_event("f6")
        return self._mod

    @property
    def F7(self) -> M:
        """Free"""
        self._mod.set_event("f7")
        return self._mod

    @property
    def F8(self) -> M:
        """Free"""
        self._mod.set_event("f8")
        return self._mod

    @property
    def F9(self) -> M:
        """Free"""
        self._mod.set_event("f9")
        return self._mod

    @property
    def F10(self) -> M:
        """Free"""
        self._mod.set_event("f10")
        return self._mod

    @property
    def F11(self) -> M:
        """Free"""
        self._mod.set_event("f11")
        return self._mod

    @property
    def F12(self) -> M:
        """Free"""
        self._mod.set_event("f12")
        return self._mod

    @property
    def HOME(self) -> M:
        """Default: beginning-of-line"""
        self._mod.set_event("home")
        return self._mod

    @property
    def LEFT(self) -> M:
        """Default: backward-char"""
        self._mod.set_event("left")
        return self._mod

    @property
    def PGDN(self) -> M:
        """Default: page-down"""
        self._mod.set_event("pgdn")
        return self._mod

    @property
    def PGUP(self) -> M:
        """Default: page-up"""
        self._mod.set_event("pgup")
        return self._mod

    @property
    def RIGHT(self) -> M:
        """Default: forward-char"""
        self._mod.set_event("right")
        return self._mod

    @property
    def RIGHT_CLICK(self) -> M:
        """Default: toggle"""
        self._mod.set_event("right-click")
        return self._mod

    @property
    def SHIFT_DOWN(self) -> M:
        """Default: preview-down"""
        self._mod.set_event("shift-down")
        return self._mod

    @property
    def SHIFT_LEFT(self) -> M:
        """Default: backward-word"""
        self._mod.set_event("shift-left")
        return self._mod

    @property
    def SHIFT_RIGHT(self) -> M:
        """Default: forward-word"""
        self._mod.set_event("shift-right")
        return self._mod

    @property
    def SHIFT_TAB(self) -> M:
        """Default: toggle+up"""
        self._mod.set_event("shift-tab")
        return self._mod

    @property
    def SHIFT_UP(self) -> M:
        """Default: preview-up"""
        self._mod.set_event("shift-up")
        return self._mod

    @property
    def TAB(self) -> M:
        """Default: toggle+down"""
        self._mod.set_event("tab")
        return self._mod

    @property
    def UP(self) -> M:
        """Default: up"""
        self._mod.set_event("up")
        return self._mod
