#!/usr/bin/env python3

# Sources:
#    * http://stackoverflow.com/q/768634/4589608
#    * http://stackoverflow.com/a/67692/4589608


# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import inspect
from importlib.machinery import SourceFileLoader

from mistool.os_use import PPath
from mistool.python_use import OrderedRecuDict


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath(__file__).parent

for parent in THIS_DIR.parents:
    if parent.name == "orPySte":
        break

PY_FILE = parent / 'orpyste/data.py'

with PY_FILE.open(
    encoding = "utf-8",
    mode     = "r"
) as f:
    SOURCE_MODULE = f.readlines()


# ------------------------------ #
# -- CHANGING A PIECE OF CODE -- #
# ------------------------------ #

print('    * Looking for the original class ``OrderedRecuDict``...')

# New code to update

source_mistool, _ = inspect.getsourcelines(OrderedRecuDict)
source_mistool    = "".join(source_mistool)


# Infos about the local and NOT the installed version !
localorpyste = SourceFileLoader(
    "orpyste.data",
    str(PY_FILE)
).load_module()

OrderedRecuDictUpdate = localorpyste.OrderedRecuDict

source_orpyste, start = inspect.getsourcelines(OrderedRecuDictUpdate)

start -= 1
end    = start + len(source_orpyste)

# Building of the new source code.

PY_TEXT = []

for nbline, line in enumerate(SOURCE_MODULE):
    if nbline < start or nbline > end:
        PY_TEXT.append(line)

    elif nbline == start:
        PY_TEXT.append(source_mistool)
        PY_TEXT.append("\n")

PY_TEXT = "".join(PY_TEXT)


# ---------------------------- #
# -- UPDATE THE PYTHON FILE -- #
# ---------------------------- #

print('    * Updating the Python file')

with PY_FILE.open(
    mode     = 'w',
    encoding = 'utf-8'
) as f:
    f.write(PY_TEXT)
