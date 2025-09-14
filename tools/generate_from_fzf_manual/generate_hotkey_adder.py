import json
from pathlib import Path

with open(Path(__file__).parent / "fzf_hotkeys.json", "r") as f:
    data = json.loads(f.read())

with open(Path(__file__).parent / "fzf_key_defaults.json", "r") as f:
    defaults = json.loads(f.read())


property_template = """
    @property
    def {func_name}(self) -> _M:
        \"\"\"{combo} ({default})\"\"\"
        return self._set_and_return_mod(\"{combo}\")"""
properties = []
for combo, func_name in data["valid"].items():
    if "\\" in combo:
        combo = combo.replace("\\", "\\\\")
    if '"' in combo:
        combo = combo.replace('"', '\\"')
    default = f"default: {df}" if (df := defaults.get(combo)) else "free"
    properties.append(property_template.format(combo=combo, func_name=func_name, default=default))

with open(Path(__file__).parent / "TriggerAdder.py", "w") as f:
    f.write(
        f"""
class HotkeyAdder[_M: OnTriggerBase]:  # _M to prevent conflict with M hotkey
    def __init__(self, mod_adder: Callable[[Hotkey], _M]):
        self._mod_adder = mod_adder

    def _set_and_return_mod(self, hotkey: Hotkey) -> _M:
        return self._mod_adder(hotkey)

{"\n".join(properties)}
"""
    )
