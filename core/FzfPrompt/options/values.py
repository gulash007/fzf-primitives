# Black magic layer
from __future__ import annotations

from typing import Literal


Layout = Literal[
    "default",
    "reverse",
    "reverse-list",
]
Border = Literal[
    "rounded",
    "sharp",
    "bold",
    "double",
    "horizontal",
    "vertical",
    "top",
    "bottom",
    "left",
    "right",
    "none",
]
Position = Literal[
    "up",
    "down",
    "left",
    "right",
]
