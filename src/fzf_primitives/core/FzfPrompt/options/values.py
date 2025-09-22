# Black magic layer
from __future__ import annotations

from typing import Literal

# custom end status for control flow
EndStatus = Literal["accept", "abort", "quit"]


# SEARCH
Scheme = Literal["default", "path", "history"]
Algorithm = Literal["v1", "v2"]
Tiebreak = Literal["length", "chunk", "pathname", "begin", "end", "index"]


# INPUT SECTION
Info = Literal["default", "right", "hidden", "inline", "inline-right"]


# DIRECTORY TRAVERSAL
WalkerValue = Literal["file", "dir", "follow", "hidden"]


# UI
Layout = Literal["default", "reverse", "reverse-list"]
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
LabelPosition = Literal["top", "bottom"]
WindowPosition = Literal["up", "down", "left", "right"]
RelativeWindowSize = Literal[
    "1%",
    "2%",
    "3%",
    "4%",
    "5%",
    "6%",
    "7%",
    "8%",
    "9%",
    "10%",
    "11%",
    "12%",
    "13%",
    "14%",
    "15%",
    "16%",
    "17%",
    "18%",
    "19%",
    "20%",
    "21%",
    "22%",
    "23%",
    "24%",
    "25%",
    "26%",
    "27%",
    "28%",
    "29%",
    "30%",
    "31%",
    "32%",
    "33%",
    "34%",
    "35%",
    "36%",
    "37%",
    "38%",
    "39%",
    "40%",
    "41%",
    "42%",
    "43%",
    "44%",
    "45%",
    "46%",
    "47%",
    "48%",
    "49%",
    "50%",
    "51%",
    "52%",
    "53%",
    "54%",
    "55%",
    "56%",
    "57%",
    "58%",
    "59%",
    "60%",
    "61%",
    "62%",
    "63%",
    "64%",
    "65%",
    "66%",
    "67%",
    "68%",
    "69%",
    "70%",
    "71%",
    "72%",
    "73%",
    "74%",
    "75%",
    "76%",
    "77%",
    "78%",
    "79%",
    "80%",
    "81%",
    "82%",
    "83%",
    "84%",
    "85%",
    "86%",
    "87%",
    "88%",
    "89%",
    "90%",
    "91%",
    "92%",
    "93%",
    "94%",
    "95%",
    "96%",
    "97%",
    "98%",
    "99%",
]
