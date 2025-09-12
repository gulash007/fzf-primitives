import json
from pathlib import Path

with open(Path(__file__).parent / "fzf_hotkeys.json", "r") as f:
    data = json.loads(f.read())


template = """
Hotkey = Literal[
{keys}
]
"""

keys = []
for combo in data["valid"].keys():
    if "\\" in combo:
        combo = combo.replace("\\", "\\\\")
    if '"' in combo:
        combo = combo.replace('"', '\\"')
    keys.append(f'    "{combo}",')

with open(Path(__file__).parent / "Hotkey.py", "w") as f:
    f.write(template.format(keys="\n".join(keys)))
