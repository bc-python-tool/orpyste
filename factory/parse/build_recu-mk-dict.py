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
from mistool.python_use import MKOrderedDict, RecuOrderedDict


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath(__file__).parent

for parent in THIS_DIR.parents:
    if parent.name == "orPyste":
        break

PY_FILE = parent / 'orpyste/parse/walk.py'

with PY_FILE.open(
    encoding = "utf-8",
    mode     = "r"
) as f:
    SOURCE_MODULE = f.readlines()


# ------------------------------ #
# -- CHANGING A PIECE OF CODE -- #
# ------------------------------ #

# Infos about the local and NOT the installed version !
localorpyste = SourceFileLoader(
    "orpyste.parse.walk",
    str(PY_FILE)
).load_module()

newcodes = []

for classdict in [MKOrderedDict, RecuOrderedDict]:
    print(
        '    * Looking for the original class ``{0}``...'.format(
            classdict.__name__
        )
    )

# Code in the last version of mistool
    source_mistool, _ = inspect.getsourcelines(classdict)
    source_mistool    = "".join(source_mistool)

    if classdict == MKOrderedDict:
        classdicttoupdate = localorpyste.MKOrderedDict

    else:
        classdicttoupdate = localorpyste.RecuOrderedDict

    source_orpyste, start = inspect.getsourcelines(classdicttoupdate)

    start -= 1
    end    = start + len(source_orpyste)

    newcodes.append((start, end, source_mistool))

newcodes.sort(key = lambda x: x[0])

starts = [x[0] for x in newcodes]
ends   = [x[1] for x in newcodes]

# Building of the new source code.

PY_TEXT = []

idstart = 0
idmax   = len(newcodes) - 1

start = starts[0]
end   = ends[0]

for nbline, line in enumerate(SOURCE_MODULE):
# Lines out of classes
    if not(start <= nbline < end):
        PY_TEXT.append(line)

        if idstart < idmax and nbline >= end:
            idstart += 1

            start = starts[idstart]
            end   = ends[idstart]

    elif nbline == start:
        PY_TEXT.append(
            newcodes[idstart][2].replace(
                "from mistool.python_use",
                "from orpyste.parse.walk",
            )
        )

PY_TEXT = "".join(PY_TEXT)


# ---------------------------- #
# -- UPDATE THE PYTHON FILE -- #
# ---------------------------- #

print('    * Updating the local Python file ``{0}``'.format(PY_FILE - parent))

with PY_FILE.open(
    mode     = 'w',
    encoding = 'utf-8'
) as f:
    f.write(PY_TEXT)
