import re

# FOCUS TAB
## open /Applications/Firefox.app/ && brotab activate --focused <tab id>


# FOCUS WINDOW
## FOCUS active TAB

# MOVE TABS TO ANOTHER WINDOW

WINDOW_ID_REGEX = re.compile("[a-z]\.\d{1,4}\.\d{1,4}")

test = "c.1.4 lkj213o lkjda"

if m := WINDOW_ID_REGEX.search(test):
    print("matched")
    print(m[0])
