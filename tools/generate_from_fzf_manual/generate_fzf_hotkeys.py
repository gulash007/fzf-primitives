import json
import os
import subprocess
from pathlib import Path

CHARS = {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "g": "G",
    "h": "H",
    "i": "I",
    "j": "J",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "U",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
    "z": "Z",
    "A": "SHIFT_A",
    "B": "SHIFT_B",
    "C": "SHIFT_C",
    "D": "SHIFT_D",
    "E": "SHIFT_E",
    "F": "SHIFT_F",
    "G": "SHIFT_G",
    "H": "SHIFT_H",
    "I": "SHIFT_I",
    "J": "SHIFT_J",
    "K": "SHIFT_K",
    "L": "SHIFT_L",
    "M": "SHIFT_M",
    "N": "SHIFT_N",
    "O": "SHIFT_O",
    "P": "SHIFT_P",
    "Q": "SHIFT_Q",
    "R": "SHIFT_R",
    "S": "SHIFT_S",
    "T": "SHIFT_T",
    "U": "SHIFT_U",
    "V": "SHIFT_V",
    "W": "SHIFT_W",
    "X": "SHIFT_X",
    "Y": "SHIFT_Y",
    "Z": "SHIFT_Z",
    "`": "BACKTICK",
    "-": "MINUS",
    "=": "EQUALS",
    "[": "SQUARE_OPEN",
    "]": "SQUARE_CLOSE",
    ";": "SEMICOLON",
    "'": "SINGLE_QUOTE",
    "\\": "BACKSLASH",
    ",": "COMMA",
    ".": "PERIOD",
    "/": "SLASH",
    "~": "TILDE",
    "_": "UNDERSCORE",
    "+": "PLUS",
    "{": "CURLY_OPEN",
    "}": "CURLY_CLOSE",
    ":": "COLON",
    '"': "DOUBLE_QUOTE",
    "|": "PIPE",
    "<": "LESS_THAN",
    ">": "GREATER_THAN",
    "?": "QUESTION",
    "§": "PARAGRAPH",
    "±": "PLUS_MINUS",
    "!": "EXCLAMATION",
    "@": "AT",
    "#": "HASH",
    "$": "DOLLAR",
    "%": "PERCENT",
    "^": "CARET",
    "&": "AMPERSAND",
    "*": "ASTERISK",
    "(": "PAREN_OPEN",
    ")": "PAREN_CLOSE",
}

SPECIAL_KEYS = {
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "enter": "ENTER",
    "return": "RETURN",
    "space": "SPACE",
    "backspace": "BACKSPACE",
    "bspace": "BSPACE",
    "bs": "BS",
    "tab": "TAB",
    "btab": "BTAB",
    "esc": "ESC",
    "delete": "DELETE",
    "del": "DEL",
    "up": "UP",
    "down": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "home": "HOME",
    "end": "END",
    "insert": "INSERT",
    "page-up": "PAGE_UP",
    "page-down": "PAGE_DOWN",
    "pgup": "PGUP",
    "pgdn": "PGDN",
    "left-click": "LEFT_CLICK",
    "right-click": "RIGHT_CLICK",
    "double-click": "DOUBLE_CLICK",
    "scroll-up": "SCROLL_UP",
    "scroll-down": "SCROLL_DOWN",
    "preview-scroll-up": "PREVIEW_SCROLL_UP",
    "preview-scroll-down": "PREVIEW_SCROLL_DOWN",
}

MODIFIERS = {
    "": "",
    "ctrl": "CTRL",
    "alt": "ALT",
    "shift": "SHIFT",
    "ctrl-alt": "CTRL_ALT",
    "alt-shift": "ALT_SHIFT",
    "ctrl-shift": "CTRL_SHIFT",
}


if __name__ == "__main__":
    valid = {}
    invalid = {}
    valid_count = 0
    invalid_count = 0
    for mod, mod_func_name in MODIFIERS.items():
        for key, key_func_name in {**CHARS, **SPECIAL_KEYS}.items():
            combo = f"{mod}-{key}" if mod else key
            combo_func_name = f"{mod_func_name}_{key_func_name}" if mod else key_func_name
            if combo_func_name[:1].isdigit():
                combo_func_name = f"NUM_{combo_func_name}"
            try:
                subprocess.check_output(["fzf", "--version", f"--bind={combo}:ignore"], stderr=subprocess.DEVNULL)
                valid_count += 1
                valid.update({combo: combo_func_name})
            except subprocess.CalledProcessError:
                invalid_count += 1
                invalid.update({combo: combo_func_name})

    PATH = Path(__file__).parent / "fzf_hotkeys.json"

    def dump_to_json_file(data, path):
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf8") as json_file:
            json.dump(data, json_file, default=lambda x: x.__dict__, indent=2, ensure_ascii=False)

    dump_to_json_file(
        {"valid": valid, "invalid": invalid, "valid_count": valid_count, "invalid_count": invalid_count}, PATH
    )

    # Load from file
    # with open(PATH, "r", encoding="utf8") as json_file:
    #     data = json.load(json_file)
