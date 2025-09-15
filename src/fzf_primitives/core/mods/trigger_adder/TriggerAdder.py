from typing import Callable

from ...FzfPrompt.options import Hotkey, Event
from ..on_trigger import OnTriggerBase


class EventAdder[M: OnTriggerBase]:
    def __init__(self, mod_adder: Callable[[Event], M]):
        self._mod_adder = mod_adder

    def _set_and_return_mod(self, trigger: Event) -> M:
        return self._mod_adder(trigger)

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
        """Triggered when the filtering for the current query is complete and the result list is ready.
        Hint: Also triggers upon new lines being piped into fzf process"""
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
    def MULTI(self) -> M:
        """Triggered when the multi-selection has changed."""
        return self._set_and_return_mod("multi")

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
        return self._set_and_return_mod("jump")

    @property
    def JUMP_CANCEL(self) -> M:
        """Triggered when jump mode is cancelled"""
        return self._set_and_return_mod("jump-cancel")

    @property
    def CLICK_HEADER(self) -> M:
        """Triggered when a mouse click occurs within the header. Sets FZF_CLICK_HEADER_LINE and FZF_CLICK_HEADER_COLUMN environment variables starting from 1. It optionally sets FZF_CLICK_HEADER_WORD and FZF_CLICK_HEADER_NTH if clicked on a word."""
        return self._set_and_return_mod("click-header")


class HotkeyAdder[_M: OnTriggerBase]:  # _M to prevent conflict with M hotkey
    def __init__(self, mod_adder: Callable[[Hotkey], _M]):
        self._mod_adder = mod_adder

    def _set_and_return_mod(self, trigger: Hotkey) -> _M:
        return self._mod_adder(trigger)

    @property
    def NUM_0(self) -> _M:
        """0 (free)"""
        return self._set_and_return_mod("0")

    @property
    def NUM_1(self) -> _M:
        """1 (free)"""
        return self._set_and_return_mod("1")

    @property
    def NUM_2(self) -> _M:
        """2 (free)"""
        return self._set_and_return_mod("2")

    @property
    def NUM_3(self) -> _M:
        """3 (free)"""
        return self._set_and_return_mod("3")

    @property
    def NUM_4(self) -> _M:
        """4 (free)"""
        return self._set_and_return_mod("4")

    @property
    def NUM_5(self) -> _M:
        """5 (free)"""
        return self._set_and_return_mod("5")

    @property
    def NUM_6(self) -> _M:
        """6 (free)"""
        return self._set_and_return_mod("6")

    @property
    def NUM_7(self) -> _M:
        """7 (free)"""
        return self._set_and_return_mod("7")

    @property
    def NUM_8(self) -> _M:
        """8 (free)"""
        return self._set_and_return_mod("8")

    @property
    def NUM_9(self) -> _M:
        """9 (free)"""
        return self._set_and_return_mod("9")

    @property
    def A(self) -> _M:
        """a (free)"""
        return self._set_and_return_mod("a")

    @property
    def B(self) -> _M:
        """b (free)"""
        return self._set_and_return_mod("b")

    @property
    def C(self) -> _M:
        """c (free)"""
        return self._set_and_return_mod("c")

    @property
    def D(self) -> _M:
        """d (free)"""
        return self._set_and_return_mod("d")

    @property
    def E(self) -> _M:
        """e (free)"""
        return self._set_and_return_mod("e")

    @property
    def F(self) -> _M:
        """f (free)"""
        return self._set_and_return_mod("f")

    @property
    def G(self) -> _M:
        """g (free)"""
        return self._set_and_return_mod("g")

    @property
    def H(self) -> _M:
        """h (free)"""
        return self._set_and_return_mod("h")

    @property
    def I(self) -> _M:
        """i (free)"""
        return self._set_and_return_mod("i")

    @property
    def J(self) -> _M:
        """j (free)"""
        return self._set_and_return_mod("j")

    @property
    def K(self) -> _M:
        """k (free)"""
        return self._set_and_return_mod("k")

    @property
    def L(self) -> _M:
        """l (free)"""
        return self._set_and_return_mod("l")

    @property
    def M(self) -> _M:
        """m (free)"""
        return self._set_and_return_mod("m")

    @property
    def N(self) -> _M:
        """n (free)"""
        return self._set_and_return_mod("n")

    @property
    def O(self) -> _M:
        """o (free)"""
        return self._set_and_return_mod("o")

    @property
    def P(self) -> _M:
        """p (free)"""
        return self._set_and_return_mod("p")

    @property
    def Q(self) -> _M:
        """q (free)"""
        return self._set_and_return_mod("q")

    @property
    def R(self) -> _M:
        """r (free)"""
        return self._set_and_return_mod("r")

    @property
    def S(self) -> _M:
        """s (free)"""
        return self._set_and_return_mod("s")

    @property
    def T(self) -> _M:
        """t (free)"""
        return self._set_and_return_mod("t")

    @property
    def U(self) -> _M:
        """u (free)"""
        return self._set_and_return_mod("u")

    @property
    def V(self) -> _M:
        """v (free)"""
        return self._set_and_return_mod("v")

    @property
    def W(self) -> _M:
        """w (free)"""
        return self._set_and_return_mod("w")

    @property
    def X(self) -> _M:
        """x (free)"""
        return self._set_and_return_mod("x")

    @property
    def Y(self) -> _M:
        """y (free)"""
        return self._set_and_return_mod("y")

    @property
    def Z(self) -> _M:
        """z (free)"""
        return self._set_and_return_mod("z")

    @property
    def SHIFT_A(self) -> _M:
        """A (free)"""
        return self._set_and_return_mod("A")

    @property
    def SHIFT_B(self) -> _M:
        """B (free)"""
        return self._set_and_return_mod("B")

    @property
    def SHIFT_C(self) -> _M:
        """C (free)"""
        return self._set_and_return_mod("C")

    @property
    def SHIFT_D(self) -> _M:
        """D (free)"""
        return self._set_and_return_mod("D")

    @property
    def SHIFT_E(self) -> _M:
        """E (free)"""
        return self._set_and_return_mod("E")

    @property
    def SHIFT_F(self) -> _M:
        """F (free)"""
        return self._set_and_return_mod("F")

    @property
    def SHIFT_G(self) -> _M:
        """G (free)"""
        return self._set_and_return_mod("G")

    @property
    def SHIFT_H(self) -> _M:
        """H (free)"""
        return self._set_and_return_mod("H")

    @property
    def SHIFT_I(self) -> _M:
        """I (free)"""
        return self._set_and_return_mod("I")

    @property
    def SHIFT_J(self) -> _M:
        """J (free)"""
        return self._set_and_return_mod("J")

    @property
    def SHIFT_K(self) -> _M:
        """K (free)"""
        return self._set_and_return_mod("K")

    @property
    def SHIFT_L(self) -> _M:
        """L (free)"""
        return self._set_and_return_mod("L")

    @property
    def SHIFT_M(self) -> _M:
        """M (free)"""
        return self._set_and_return_mod("M")

    @property
    def SHIFT_N(self) -> _M:
        """N (free)"""
        return self._set_and_return_mod("N")

    @property
    def SHIFT_O(self) -> _M:
        """O (free)"""
        return self._set_and_return_mod("O")

    @property
    def SHIFT_P(self) -> _M:
        """P (free)"""
        return self._set_and_return_mod("P")

    @property
    def SHIFT_Q(self) -> _M:
        """Q (free)"""
        return self._set_and_return_mod("Q")

    @property
    def SHIFT_R(self) -> _M:
        """R (free)"""
        return self._set_and_return_mod("R")

    @property
    def SHIFT_S(self) -> _M:
        """S (free)"""
        return self._set_and_return_mod("S")

    @property
    def SHIFT_T(self) -> _M:
        """T (free)"""
        return self._set_and_return_mod("T")

    @property
    def SHIFT_U(self) -> _M:
        """U (free)"""
        return self._set_and_return_mod("U")

    @property
    def SHIFT_V(self) -> _M:
        """V (free)"""
        return self._set_and_return_mod("V")

    @property
    def SHIFT_W(self) -> _M:
        """W (free)"""
        return self._set_and_return_mod("W")

    @property
    def SHIFT_X(self) -> _M:
        """X (free)"""
        return self._set_and_return_mod("X")

    @property
    def SHIFT_Y(self) -> _M:
        """Y (free)"""
        return self._set_and_return_mod("Y")

    @property
    def SHIFT_Z(self) -> _M:
        """Z (free)"""
        return self._set_and_return_mod("Z")

    @property
    def BACKTICK(self) -> _M:
        """` (free)"""
        return self._set_and_return_mod("`")

    @property
    def MINUS(self) -> _M:
        """- (free)"""
        return self._set_and_return_mod("-")

    @property
    def EQUALS(self) -> _M:
        """= (free)"""
        return self._set_and_return_mod("=")

    @property
    def SQUARE_OPEN(self) -> _M:
        """[ (free)"""
        return self._set_and_return_mod("[")

    @property
    def SQUARE_CLOSE(self) -> _M:
        """] (free)"""
        return self._set_and_return_mod("]")

    @property
    def SEMICOLON(self) -> _M:
        """; (free)"""
        return self._set_and_return_mod(";")

    @property
    def SINGLE_QUOTE(self) -> _M:
        """' (free)"""
        return self._set_and_return_mod("'")

    @property
    def BACKSLASH(self) -> _M:
        """\\ (free)"""
        return self._set_and_return_mod("\\")

    @property
    def COMMA(self) -> _M:
        """, (free)"""
        return self._set_and_return_mod(",")

    @property
    def PERIOD(self) -> _M:
        """. (free)"""
        return self._set_and_return_mod(".")

    @property
    def SLASH(self) -> _M:
        """/ (free)"""
        return self._set_and_return_mod("/")

    @property
    def TILDE(self) -> _M:
        """~ (free)"""
        return self._set_and_return_mod("~")

    @property
    def UNDERSCORE(self) -> _M:
        """_ (free)"""
        return self._set_and_return_mod("_")

    @property
    def PLUS(self) -> _M:
        """+ (free)"""
        return self._set_and_return_mod("+")

    @property
    def CURLY_OPEN(self) -> _M:
        """{ (free)"""
        return self._set_and_return_mod("{")

    @property
    def CURLY_CLOSE(self) -> _M:
        """} (free)"""
        return self._set_and_return_mod("}")

    @property
    def COLON(self) -> _M:
        """: (free)"""
        return self._set_and_return_mod(":")

    @property
    def DOUBLE_QUOTE(self) -> _M:
        """\" (free)"""
        return self._set_and_return_mod('"')

    @property
    def PIPE(self) -> _M:
        """| (free)"""
        return self._set_and_return_mod("|")

    @property
    def LESS_THAN(self) -> _M:
        """< (free)"""
        return self._set_and_return_mod("<")

    @property
    def GREATER_THAN(self) -> _M:
        """> (free)"""
        return self._set_and_return_mod(">")

    @property
    def QUESTION(self) -> _M:
        """? (free)"""
        return self._set_and_return_mod("?")

    @property
    def PARAGRAPH(self) -> _M:
        """§ (free)"""
        return self._set_and_return_mod("§")

    @property
    def PLUS_MINUS(self) -> _M:
        """± (free)"""
        return self._set_and_return_mod("±")

    @property
    def EXCLAMATION(self) -> _M:
        """! (free)"""
        return self._set_and_return_mod("!")

    @property
    def AT(self) -> _M:
        """@ (free)"""
        return self._set_and_return_mod("@")

    @property
    def HASH(self) -> _M:
        """# (free)"""
        return self._set_and_return_mod("#")

    @property
    def DOLLAR(self) -> _M:
        """$ (free)"""
        return self._set_and_return_mod("$")

    @property
    def PERCENT(self) -> _M:
        """% (free)"""
        return self._set_and_return_mod("%")

    @property
    def CARET(self) -> _M:
        """^ (free)"""
        return self._set_and_return_mod("^")

    @property
    def AMPERSAND(self) -> _M:
        """& (free)"""
        return self._set_and_return_mod("&")

    @property
    def ASTERISK(self) -> _M:
        """* (free)"""
        return self._set_and_return_mod("*")

    @property
    def PAREN_OPEN(self) -> _M:
        """( (free)"""
        return self._set_and_return_mod("(")

    @property
    def PAREN_CLOSE(self) -> _M:
        """) (free)"""
        return self._set_and_return_mod(")")

    @property
    def F1(self) -> _M:
        """f1 (free)"""
        return self._set_and_return_mod("f1")

    @property
    def F2(self) -> _M:
        """f2 (free)"""
        return self._set_and_return_mod("f2")

    @property
    def F3(self) -> _M:
        """f3 (free)"""
        return self._set_and_return_mod("f3")

    @property
    def F4(self) -> _M:
        """f4 (free)"""
        return self._set_and_return_mod("f4")

    @property
    def F5(self) -> _M:
        """f5 (free)"""
        return self._set_and_return_mod("f5")

    @property
    def F6(self) -> _M:
        """f6 (free)"""
        return self._set_and_return_mod("f6")

    @property
    def F7(self) -> _M:
        """f7 (free)"""
        return self._set_and_return_mod("f7")

    @property
    def F8(self) -> _M:
        """f8 (free)"""
        return self._set_and_return_mod("f8")

    @property
    def F9(self) -> _M:
        """f9 (free)"""
        return self._set_and_return_mod("f9")

    @property
    def F10(self) -> _M:
        """f10 (free)"""
        return self._set_and_return_mod("f10")

    @property
    def F11(self) -> _M:
        """f11 (free)"""
        return self._set_and_return_mod("f11")

    @property
    def F12(self) -> _M:
        """f12 (free)"""
        return self._set_and_return_mod("f12")

    @property
    def ENTER(self) -> _M:
        """enter (default: accept)"""
        return self._set_and_return_mod("enter")

    @property
    def RETURN(self) -> _M:
        """return (default: accept)"""
        return self._set_and_return_mod("return")

    @property
    def SPACE(self) -> _M:
        """space (free)"""
        return self._set_and_return_mod("space")

    @property
    def BACKSPACE(self) -> _M:
        """backspace (default: backward-delete-char)"""
        return self._set_and_return_mod("backspace")

    @property
    def BSPACE(self) -> _M:
        """bspace (default: backward-delete-char)"""
        return self._set_and_return_mod("bspace")

    @property
    def BS(self) -> _M:
        """bs (default: backward-delete-char)"""
        return self._set_and_return_mod("bs")

    @property
    def TAB(self) -> _M:
        """tab (default: toggle+down)"""
        return self._set_and_return_mod("tab")

    @property
    def BTAB(self) -> _M:
        """btab (default: toggle+up)"""
        return self._set_and_return_mod("btab")

    @property
    def ESC(self) -> _M:
        """esc (default: abort)"""
        return self._set_and_return_mod("esc")

    @property
    def DELETE(self) -> _M:
        """delete (default: delete-char)"""
        return self._set_and_return_mod("delete")

    @property
    def DEL(self) -> _M:
        """del (default: delete-char)"""
        return self._set_and_return_mod("del")

    @property
    def UP(self) -> _M:
        """up (default: up)"""
        return self._set_and_return_mod("up")

    @property
    def DOWN(self) -> _M:
        """down (default: down)"""
        return self._set_and_return_mod("down")

    @property
    def LEFT(self) -> _M:
        """left (default: backward-char)"""
        return self._set_and_return_mod("left")

    @property
    def RIGHT(self) -> _M:
        """right (default: forward-char)"""
        return self._set_and_return_mod("right")

    @property
    def HOME(self) -> _M:
        """home (default: beginning-of-line)"""
        return self._set_and_return_mod("home")

    @property
    def END(self) -> _M:
        """end (default: end-of-line)"""
        return self._set_and_return_mod("end")

    @property
    def INSERT(self) -> _M:
        """insert (free)"""
        return self._set_and_return_mod("insert")

    @property
    def PAGE_UP(self) -> _M:
        """page-up (default: page-up)"""
        return self._set_and_return_mod("page-up")

    @property
    def PAGE_DOWN(self) -> _M:
        """page-down (default: page-down)"""
        return self._set_and_return_mod("page-down")

    @property
    def PGUP(self) -> _M:
        """pgup (default: page-up)"""
        return self._set_and_return_mod("pgup")

    @property
    def PGDN(self) -> _M:
        """pgdn (default: page-down)"""
        return self._set_and_return_mod("pgdn")

    @property
    def LEFT_CLICK(self) -> _M:
        """left-click (free)"""
        return self._set_and_return_mod("left-click")

    @property
    def RIGHT_CLICK(self) -> _M:
        """right-click (default: toggle)"""
        return self._set_and_return_mod("right-click")

    @property
    def DOUBLE_CLICK(self) -> _M:
        """double-click (default: accept)"""
        return self._set_and_return_mod("double-click")

    @property
    def SCROLL_UP(self) -> _M:
        """scroll-up (free)"""
        return self._set_and_return_mod("scroll-up")

    @property
    def SCROLL_DOWN(self) -> _M:
        """scroll-down (free)"""
        return self._set_and_return_mod("scroll-down")

    @property
    def PREVIEW_SCROLL_UP(self) -> _M:
        """preview-scroll-up (free)"""
        return self._set_and_return_mod("preview-scroll-up")

    @property
    def PREVIEW_SCROLL_DOWN(self) -> _M:
        """preview-scroll-down (free)"""
        return self._set_and_return_mod("preview-scroll-down")

    @property
    def CTRL_6(self) -> _M:
        """ctrl-6 (free)"""
        return self._set_and_return_mod("ctrl-6")

    @property
    def CTRL_A(self) -> _M:
        """ctrl-a (default: beginning-of-line)"""
        return self._set_and_return_mod("ctrl-a")

    @property
    def CTRL_B(self) -> _M:
        """ctrl-b (default: backward-char). ❗ May conflict with tmux prefix key."""
        return self._set_and_return_mod("ctrl-b")

    @property
    def CTRL_C(self) -> _M:
        """ctrl-c (default: abort)"""
        return self._set_and_return_mod("ctrl-c")

    @property
    def CTRL_D(self) -> _M:
        """ctrl-d (default: delete-char/eof)"""
        return self._set_and_return_mod("ctrl-d")

    @property
    def CTRL_E(self) -> _M:
        """ctrl-e (default: end-of-line)"""
        return self._set_and_return_mod("ctrl-e")

    @property
    def CTRL_F(self) -> _M:
        """ctrl-f (default: forward-char)"""
        return self._set_and_return_mod("ctrl-f")

    @property
    def CTRL_G(self) -> _M:
        """ctrl-g (default: abort)"""
        return self._set_and_return_mod("ctrl-g")

    @property
    def CTRL_H(self) -> _M:
        """ctrl-h (default: backward-delete-char)"""
        return self._set_and_return_mod("ctrl-h")

    @property
    def CTRL_I(self) -> _M:
        """ctrl-i (default: toggle+down)"""
        return self._set_and_return_mod("ctrl-i")

    @property
    def CTRL_J(self) -> _M:
        """ctrl-j (default: down)"""
        return self._set_and_return_mod("ctrl-j")

    @property
    def CTRL_K(self) -> _M:
        """ctrl-k (default: up)"""
        return self._set_and_return_mod("ctrl-k")

    @property
    def CTRL_L(self) -> _M:
        """ctrl-l (default: clear-screen)"""
        return self._set_and_return_mod("ctrl-l")

    @property
    def CTRL_M(self) -> _M:
        """ctrl-m (default: accept)"""
        return self._set_and_return_mod("ctrl-m")

    @property
    def CTRL_N(self) -> _M:
        """ctrl-n (default: down)"""
        return self._set_and_return_mod("ctrl-n")

    @property
    def CTRL_O(self) -> _M:
        """ctrl-o (free)"""
        return self._set_and_return_mod("ctrl-o")

    @property
    def CTRL_P(self) -> _M:
        """ctrl-p (default: up)"""
        return self._set_and_return_mod("ctrl-p")

    @property
    def CTRL_Q(self) -> _M:
        """ctrl-q (default: abort)"""
        return self._set_and_return_mod("ctrl-q")

    @property
    def CTRL_R(self) -> _M:
        """ctrl-r (free)"""
        return self._set_and_return_mod("ctrl-r")

    @property
    def CTRL_S(self) -> _M:
        """ctrl-s (free)"""
        return self._set_and_return_mod("ctrl-s")

    @property
    def CTRL_T(self) -> _M:
        """ctrl-t (free)"""
        return self._set_and_return_mod("ctrl-t")

    @property
    def CTRL_U(self) -> _M:
        """ctrl-u (default: unix-line-discard)"""
        return self._set_and_return_mod("ctrl-u")

    @property
    def CTRL_V(self) -> _M:
        """ctrl-v (free)"""
        return self._set_and_return_mod("ctrl-v")

    @property
    def CTRL_W(self) -> _M:
        """ctrl-w (default: unix-word-rubout)"""
        return self._set_and_return_mod("ctrl-w")

    @property
    def CTRL_X(self) -> _M:
        """ctrl-x (free)"""
        return self._set_and_return_mod("ctrl-x")

    @property
    def CTRL_Y(self) -> _M:
        """ctrl-y (default: yank)"""
        return self._set_and_return_mod("ctrl-y")

    @property
    def CTRL_Z(self) -> _M:
        """ctrl-z (free)"""
        return self._set_and_return_mod("ctrl-z")

    @property
    def CTRL_SQUARE_CLOSE(self) -> _M:
        """ctrl-] (free)"""
        return self._set_and_return_mod("ctrl-]")

    @property
    def CTRL_BACKSLASH(self) -> _M:
        """ctrl-\\ (free)"""
        return self._set_and_return_mod("ctrl-\\")

    @property
    def CTRL_SLASH(self) -> _M:
        """ctrl-/ (default: toggle-wrap)"""
        return self._set_and_return_mod("ctrl-/")

    @property
    def CTRL_UNDERSCORE(self) -> _M:
        """ctrl-_ (free)"""
        return self._set_and_return_mod("ctrl-_")

    @property
    def CTRL_CARET(self) -> _M:
        """ctrl-^ (free)"""
        return self._set_and_return_mod("ctrl-^")

    @property
    def CTRL_SPACE(self) -> _M:
        """ctrl-space (free)"""
        return self._set_and_return_mod("ctrl-space")

    @property
    def CTRL_DELETE(self) -> _M:
        """ctrl-delete (free)"""
        return self._set_and_return_mod("ctrl-delete")

    @property
    def ALT_0(self) -> _M:
        """alt-0 (free)"""
        return self._set_and_return_mod("alt-0")

    @property
    def ALT_1(self) -> _M:
        """alt-1 (free)"""
        return self._set_and_return_mod("alt-1")

    @property
    def ALT_2(self) -> _M:
        """alt-2 (free)"""
        return self._set_and_return_mod("alt-2")

    @property
    def ALT_3(self) -> _M:
        """alt-3 (free)"""
        return self._set_and_return_mod("alt-3")

    @property
    def ALT_4(self) -> _M:
        """alt-4 (free)"""
        return self._set_and_return_mod("alt-4")

    @property
    def ALT_5(self) -> _M:
        """alt-5 (free)"""
        return self._set_and_return_mod("alt-5")

    @property
    def ALT_6(self) -> _M:
        """alt-6 (free)"""
        return self._set_and_return_mod("alt-6")

    @property
    def ALT_7(self) -> _M:
        """alt-7 (free)"""
        return self._set_and_return_mod("alt-7")

    @property
    def ALT_8(self) -> _M:
        """alt-8 (free)"""
        return self._set_and_return_mod("alt-8")

    @property
    def ALT_9(self) -> _M:
        """alt-9 (free)"""
        return self._set_and_return_mod("alt-9")

    @property
    def ALT_A(self) -> _M:
        """alt-a (free)"""
        return self._set_and_return_mod("alt-a")

    @property
    def ALT_B(self) -> _M:
        """alt-b (default: backward-word)"""
        return self._set_and_return_mod("alt-b")

    @property
    def ALT_C(self) -> _M:
        """alt-c (free)"""
        return self._set_and_return_mod("alt-c")

    @property
    def ALT_D(self) -> _M:
        """alt-d (default: kill-word)"""
        return self._set_and_return_mod("alt-d")

    @property
    def ALT_E(self) -> _M:
        """alt-e (free)"""
        return self._set_and_return_mod("alt-e")

    @property
    def ALT_F(self) -> _M:
        """alt-f (default: forward-word)"""
        return self._set_and_return_mod("alt-f")

    @property
    def ALT_G(self) -> _M:
        """alt-g (free)"""
        return self._set_and_return_mod("alt-g")

    @property
    def ALT_H(self) -> _M:
        """alt-h (free)"""
        return self._set_and_return_mod("alt-h")

    @property
    def ALT_I(self) -> _M:
        """alt-i (free)"""
        return self._set_and_return_mod("alt-i")

    @property
    def ALT_J(self) -> _M:
        """alt-j (free)"""
        return self._set_and_return_mod("alt-j")

    @property
    def ALT_K(self) -> _M:
        """alt-k (free)"""
        return self._set_and_return_mod("alt-k")

    @property
    def ALT_L(self) -> _M:
        """alt-l (free)"""
        return self._set_and_return_mod("alt-l")

    @property
    def ALT_M(self) -> _M:
        """alt-m (free)"""
        return self._set_and_return_mod("alt-m")

    @property
    def ALT_N(self) -> _M:
        """alt-n (free)"""
        return self._set_and_return_mod("alt-n")

    @property
    def ALT_O(self) -> _M:
        """alt-o (free)"""
        return self._set_and_return_mod("alt-o")

    @property
    def ALT_P(self) -> _M:
        """alt-p (free)"""
        return self._set_and_return_mod("alt-p")

    @property
    def ALT_Q(self) -> _M:
        """alt-q (free)"""
        return self._set_and_return_mod("alt-q")

    @property
    def ALT_R(self) -> _M:
        """alt-r (free)"""
        return self._set_and_return_mod("alt-r")

    @property
    def ALT_S(self) -> _M:
        """alt-s (free)"""
        return self._set_and_return_mod("alt-s")

    @property
    def ALT_T(self) -> _M:
        """alt-t (free)"""
        return self._set_and_return_mod("alt-t")

    @property
    def ALT_U(self) -> _M:
        """alt-u (free)"""
        return self._set_and_return_mod("alt-u")

    @property
    def ALT_V(self) -> _M:
        """alt-v (free)"""
        return self._set_and_return_mod("alt-v")

    @property
    def ALT_W(self) -> _M:
        """alt-w (free)"""
        return self._set_and_return_mod("alt-w")

    @property
    def ALT_X(self) -> _M:
        """alt-x (free)"""
        return self._set_and_return_mod("alt-x")

    @property
    def ALT_Y(self) -> _M:
        """alt-y (free)"""
        return self._set_and_return_mod("alt-y")

    @property
    def ALT_Z(self) -> _M:
        """alt-z (free)"""
        return self._set_and_return_mod("alt-z")

    @property
    def ALT_SHIFT_A(self) -> _M:
        """alt-A (free)"""
        return self._set_and_return_mod("alt-A")

    @property
    def ALT_SHIFT_B(self) -> _M:
        """alt-B (free)"""
        return self._set_and_return_mod("alt-B")

    @property
    def ALT_SHIFT_C(self) -> _M:
        """alt-C (free)"""
        return self._set_and_return_mod("alt-C")

    @property
    def ALT_SHIFT_D(self) -> _M:
        """alt-D (free)"""
        return self._set_and_return_mod("alt-D")

    @property
    def ALT_SHIFT_E(self) -> _M:
        """alt-E (free)"""
        return self._set_and_return_mod("alt-E")

    @property
    def ALT_SHIFT_F(self) -> _M:
        """alt-F (free)"""
        return self._set_and_return_mod("alt-F")

    @property
    def ALT_SHIFT_G(self) -> _M:
        """alt-G (free)"""
        return self._set_and_return_mod("alt-G")

    @property
    def ALT_SHIFT_H(self) -> _M:
        """alt-H (free)"""
        return self._set_and_return_mod("alt-H")

    @property
    def ALT_SHIFT_I(self) -> _M:
        """alt-I (free)"""
        return self._set_and_return_mod("alt-I")

    @property
    def ALT_SHIFT_J(self) -> _M:
        """alt-J (free)"""
        return self._set_and_return_mod("alt-J")

    @property
    def ALT_SHIFT_K(self) -> _M:
        """alt-K (free)"""
        return self._set_and_return_mod("alt-K")

    @property
    def ALT_SHIFT_L(self) -> _M:
        """alt-L (free)"""
        return self._set_and_return_mod("alt-L")

    @property
    def ALT_SHIFT_M(self) -> _M:
        """alt-M (free)"""
        return self._set_and_return_mod("alt-M")

    @property
    def ALT_SHIFT_N(self) -> _M:
        """alt-N (free)"""
        return self._set_and_return_mod("alt-N")

    @property
    def ALT_SHIFT_O(self) -> _M:
        """alt-O (free)"""
        return self._set_and_return_mod("alt-O")

    @property
    def ALT_SHIFT_P(self) -> _M:
        """alt-P (free)"""
        return self._set_and_return_mod("alt-P")

    @property
    def ALT_SHIFT_Q(self) -> _M:
        """alt-Q (free)"""
        return self._set_and_return_mod("alt-Q")

    @property
    def ALT_SHIFT_R(self) -> _M:
        """alt-R (free)"""
        return self._set_and_return_mod("alt-R")

    @property
    def ALT_SHIFT_S(self) -> _M:
        """alt-S (free)"""
        return self._set_and_return_mod("alt-S")

    @property
    def ALT_SHIFT_T(self) -> _M:
        """alt-T (free)"""
        return self._set_and_return_mod("alt-T")

    @property
    def ALT_SHIFT_U(self) -> _M:
        """alt-U (free)"""
        return self._set_and_return_mod("alt-U")

    @property
    def ALT_SHIFT_V(self) -> _M:
        """alt-V (free)"""
        return self._set_and_return_mod("alt-V")

    @property
    def ALT_SHIFT_W(self) -> _M:
        """alt-W (free)"""
        return self._set_and_return_mod("alt-W")

    @property
    def ALT_SHIFT_X(self) -> _M:
        """alt-X (free)"""
        return self._set_and_return_mod("alt-X")

    @property
    def ALT_SHIFT_Y(self) -> _M:
        """alt-Y (free)"""
        return self._set_and_return_mod("alt-Y")

    @property
    def ALT_SHIFT_Z(self) -> _M:
        """alt-Z (free)"""
        return self._set_and_return_mod("alt-Z")

    @property
    def ALT_BACKTICK(self) -> _M:
        """alt-` (free)"""
        return self._set_and_return_mod("alt-`")

    @property
    def ALT_MINUS(self) -> _M:
        """alt-- (free)"""
        return self._set_and_return_mod("alt--")

    @property
    def ALT_EQUALS(self) -> _M:
        """alt-= (free)"""
        return self._set_and_return_mod("alt-=")

    @property
    def ALT_SQUARE_OPEN(self) -> _M:
        """alt-[ (free)"""
        return self._set_and_return_mod("alt-[")

    @property
    def ALT_SQUARE_CLOSE(self) -> _M:
        """alt-] (free)"""
        return self._set_and_return_mod("alt-]")

    @property
    def ALT_SEMICOLON(self) -> _M:
        """alt-; (free)"""
        return self._set_and_return_mod("alt-;")

    @property
    def ALT_SINGLE_QUOTE(self) -> _M:
        """alt-' (free)"""
        return self._set_and_return_mod("alt-'")

    @property
    def ALT_BACKSLASH(self) -> _M:
        """alt-\\ (free)"""
        return self._set_and_return_mod("alt-\\")

    @property
    def ALT_COMMA(self) -> _M:
        """alt-, (free)"""
        return self._set_and_return_mod("alt-,")

    @property
    def ALT_PERIOD(self) -> _M:
        """alt-. (free)"""
        return self._set_and_return_mod("alt-.")

    @property
    def ALT_SLASH(self) -> _M:
        """alt-/ (default: toggle-wrap)"""
        return self._set_and_return_mod("alt-/")

    @property
    def ALT_TILDE(self) -> _M:
        """alt-~ (free)"""
        return self._set_and_return_mod("alt-~")

    @property
    def ALT_UNDERSCORE(self) -> _M:
        """alt-_ (free)"""
        return self._set_and_return_mod("alt-_")

    @property
    def ALT_PLUS(self) -> _M:
        """alt-+ (free)"""
        return self._set_and_return_mod("alt-+")

    @property
    def ALT_CURLY_OPEN(self) -> _M:
        """alt-{ (free)"""
        return self._set_and_return_mod("alt-{")

    @property
    def ALT_CURLY_CLOSE(self) -> _M:
        """alt-} (free)"""
        return self._set_and_return_mod("alt-}")

    @property
    def ALT_COLON(self) -> _M:
        """alt-: (free)"""
        return self._set_and_return_mod("alt-:")

    @property
    def ALT_DOUBLE_QUOTE(self) -> _M:
        """alt-\" (free)"""
        return self._set_and_return_mod('alt-"')

    @property
    def ALT_PIPE(self) -> _M:
        """alt-| (free)"""
        return self._set_and_return_mod("alt-|")

    @property
    def ALT_LESS_THAN(self) -> _M:
        """alt-< (free)"""
        return self._set_and_return_mod("alt-<")

    @property
    def ALT_GREATER_THAN(self) -> _M:
        """alt-> (free)"""
        return self._set_and_return_mod("alt->")

    @property
    def ALT_QUESTION(self) -> _M:
        """alt-? (free)"""
        return self._set_and_return_mod("alt-?")

    @property
    def ALT_PARAGRAPH(self) -> _M:
        """alt-§ (free)"""
        return self._set_and_return_mod("alt-§")

    @property
    def ALT_PLUS_MINUS(self) -> _M:
        """alt-± (free)"""
        return self._set_and_return_mod("alt-±")

    @property
    def ALT_EXCLAMATION(self) -> _M:
        """alt-! (free)"""
        return self._set_and_return_mod("alt-!")

    @property
    def ALT_AT(self) -> _M:
        """alt-@ (free)"""
        return self._set_and_return_mod("alt-@")

    @property
    def ALT_HASH(self) -> _M:
        """alt-# (free)"""
        return self._set_and_return_mod("alt-#")

    @property
    def ALT_DOLLAR(self) -> _M:
        """alt-$ (free)"""
        return self._set_and_return_mod("alt-$")

    @property
    def ALT_PERCENT(self) -> _M:
        """alt-% (free)"""
        return self._set_and_return_mod("alt-%")

    @property
    def ALT_CARET(self) -> _M:
        """alt-^ (free)"""
        return self._set_and_return_mod("alt-^")

    @property
    def ALT_AMPERSAND(self) -> _M:
        """alt-& (free)"""
        return self._set_and_return_mod("alt-&")

    @property
    def ALT_ASTERISK(self) -> _M:
        """alt-* (free)"""
        return self._set_and_return_mod("alt-*")

    @property
    def ALT_PAREN_OPEN(self) -> _M:
        """alt-( (free)"""
        return self._set_and_return_mod("alt-(")

    @property
    def ALT_PAREN_CLOSE(self) -> _M:
        """alt-) (free)"""
        return self._set_and_return_mod("alt-)")

    @property
    def ALT_ENTER(self) -> _M:
        """alt-enter (free)"""
        return self._set_and_return_mod("alt-enter")

    @property
    def ALT_RETURN(self) -> _M:
        """alt-return (free)"""
        return self._set_and_return_mod("alt-return")

    @property
    def ALT_SPACE(self) -> _M:
        """alt-space (free)"""
        return self._set_and_return_mod("alt-space")

    @property
    def ALT_BACKSPACE(self) -> _M:
        """alt-backspace (default: backward-kill-word)"""
        return self._set_and_return_mod("alt-backspace")

    @property
    def ALT_BSPACE(self) -> _M:
        """alt-bspace (default: backward-kill-word)"""
        return self._set_and_return_mod("alt-bspace")

    @property
    def ALT_BS(self) -> _M:
        """alt-bs (default: backward-kill-word)"""
        return self._set_and_return_mod("alt-bs")

    @property
    def ALT_UP(self) -> _M:
        """alt-up (free)"""
        return self._set_and_return_mod("alt-up")

    @property
    def ALT_DOWN(self) -> _M:
        """alt-down (free)"""
        return self._set_and_return_mod("alt-down")

    @property
    def ALT_LEFT(self) -> _M:
        """alt-left (free)"""
        return self._set_and_return_mod("alt-left")

    @property
    def ALT_RIGHT(self) -> _M:
        """alt-right (free)"""
        return self._set_and_return_mod("alt-right")

    @property
    def SHIFT_TAB(self) -> _M:
        """shift-tab (default: toggle+up)"""
        return self._set_and_return_mod("shift-tab")

    @property
    def SHIFT_DELETE(self) -> _M:
        """shift-delete (free)"""
        return self._set_and_return_mod("shift-delete")

    @property
    def SHIFT_UP(self) -> _M:
        """shift-up (default: preview-up)"""
        return self._set_and_return_mod("shift-up")

    @property
    def SHIFT_DOWN(self) -> _M:
        """shift-down (default: preview-down)"""
        return self._set_and_return_mod("shift-down")

    @property
    def SHIFT_LEFT(self) -> _M:
        """shift-left (default: backward-word)"""
        return self._set_and_return_mod("shift-left")

    @property
    def SHIFT_RIGHT(self) -> _M:
        """shift-right (default: forward-word)"""
        return self._set_and_return_mod("shift-right")

    @property
    def SHIFT_LEFT_CLICK(self) -> _M:
        """shift-left-click (free)"""
        return self._set_and_return_mod("shift-left-click")

    @property
    def SHIFT_RIGHT_CLICK(self) -> _M:
        """shift-right-click (free)"""
        return self._set_and_return_mod("shift-right-click")

    @property
    def SHIFT_SCROLL_UP(self) -> _M:
        """shift-scroll-up (free)"""
        return self._set_and_return_mod("shift-scroll-up")

    @property
    def SHIFT_SCROLL_DOWN(self) -> _M:
        """shift-scroll-down (free)"""
        return self._set_and_return_mod("shift-scroll-down")

    @property
    def CTRL_ALT_A(self) -> _M:
        """ctrl-alt-a (free)"""
        return self._set_and_return_mod("ctrl-alt-a")

    @property
    def CTRL_ALT_B(self) -> _M:
        """ctrl-alt-b (free)"""
        return self._set_and_return_mod("ctrl-alt-b")

    @property
    def CTRL_ALT_C(self) -> _M:
        """ctrl-alt-c (free)"""
        return self._set_and_return_mod("ctrl-alt-c")

    @property
    def CTRL_ALT_D(self) -> _M:
        """ctrl-alt-d (free)"""
        return self._set_and_return_mod("ctrl-alt-d")

    @property
    def CTRL_ALT_E(self) -> _M:
        """ctrl-alt-e (free)"""
        return self._set_and_return_mod("ctrl-alt-e")

    @property
    def CTRL_ALT_F(self) -> _M:
        """ctrl-alt-f (free)"""
        return self._set_and_return_mod("ctrl-alt-f")

    @property
    def CTRL_ALT_G(self) -> _M:
        """ctrl-alt-g (free)"""
        return self._set_and_return_mod("ctrl-alt-g")

    @property
    def CTRL_ALT_H(self) -> _M:
        """ctrl-alt-h (free)"""
        return self._set_and_return_mod("ctrl-alt-h")

    @property
    def CTRL_ALT_I(self) -> _M:
        """ctrl-alt-i (free)"""
        return self._set_and_return_mod("ctrl-alt-i")

    @property
    def CTRL_ALT_J(self) -> _M:
        """ctrl-alt-j (free)"""
        return self._set_and_return_mod("ctrl-alt-j")

    @property
    def CTRL_ALT_K(self) -> _M:
        """ctrl-alt-k (free)"""
        return self._set_and_return_mod("ctrl-alt-k")

    @property
    def CTRL_ALT_L(self) -> _M:
        """ctrl-alt-l (free)"""
        return self._set_and_return_mod("ctrl-alt-l")

    @property
    def CTRL_ALT_M(self) -> _M:
        """ctrl-alt-m (free)"""
        return self._set_and_return_mod("ctrl-alt-m")

    @property
    def CTRL_ALT_N(self) -> _M:
        """ctrl-alt-n (free)"""
        return self._set_and_return_mod("ctrl-alt-n")

    @property
    def CTRL_ALT_O(self) -> _M:
        """ctrl-alt-o (free)"""
        return self._set_and_return_mod("ctrl-alt-o")

    @property
    def CTRL_ALT_P(self) -> _M:
        """ctrl-alt-p (free)"""
        return self._set_and_return_mod("ctrl-alt-p")

    @property
    def CTRL_ALT_Q(self) -> _M:
        """ctrl-alt-q (free)"""
        return self._set_and_return_mod("ctrl-alt-q")

    @property
    def CTRL_ALT_R(self) -> _M:
        """ctrl-alt-r (free)"""
        return self._set_and_return_mod("ctrl-alt-r")

    @property
    def CTRL_ALT_S(self) -> _M:
        """ctrl-alt-s (free)"""
        return self._set_and_return_mod("ctrl-alt-s")

    @property
    def CTRL_ALT_T(self) -> _M:
        """ctrl-alt-t (free)"""
        return self._set_and_return_mod("ctrl-alt-t")

    @property
    def CTRL_ALT_U(self) -> _M:
        """ctrl-alt-u (free)"""
        return self._set_and_return_mod("ctrl-alt-u")

    @property
    def CTRL_ALT_V(self) -> _M:
        """ctrl-alt-v (free)"""
        return self._set_and_return_mod("ctrl-alt-v")

    @property
    def CTRL_ALT_W(self) -> _M:
        """ctrl-alt-w (free)"""
        return self._set_and_return_mod("ctrl-alt-w")

    @property
    def CTRL_ALT_X(self) -> _M:
        """ctrl-alt-x (free)"""
        return self._set_and_return_mod("ctrl-alt-x")

    @property
    def CTRL_ALT_Y(self) -> _M:
        """ctrl-alt-y (free)"""
        return self._set_and_return_mod("ctrl-alt-y")

    @property
    def CTRL_ALT_Z(self) -> _M:
        """ctrl-alt-z (free)"""
        return self._set_and_return_mod("ctrl-alt-z")

    @property
    def ALT_SHIFT_UP(self) -> _M:
        """alt-shift-up (free)"""
        return self._set_and_return_mod("alt-shift-up")

    @property
    def ALT_SHIFT_DOWN(self) -> _M:
        """alt-shift-down (free)"""
        return self._set_and_return_mod("alt-shift-down")

    @property
    def ALT_SHIFT_LEFT(self) -> _M:
        """alt-shift-left (free)"""
        return self._set_and_return_mod("alt-shift-left")

    @property
    def ALT_SHIFT_RIGHT(self) -> _M:
        """alt-shift-right (free)"""
        return self._set_and_return_mod("alt-shift-right")


class TriggerAdder[M: OnTriggerBase](HotkeyAdder[M], EventAdder[M]):
    def __init__(self, mod_adder: Callable[[Hotkey | Event], M]):
        self._mod_adder = mod_adder

    def _set_and_return_mod(self, trigger: Hotkey | Event) -> M:
        return self._mod_adder(trigger)
