#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import json

from hypothesis import given
import hypothesis.strategies as st
from mistool.os_use import PPath


# ------------------- #
# -- MODULE TESTED -- #
# ------------------- #

from orpyste.tools import ioview


# ----------------------- #
# -- GENERAL CONSTANTS -- #
# ----------------------- #

THIS_DIR = PPath(__file__).parent

IOVIEW_CLASS = ioview.IOView
MODES_PATHS  = [
    ("list", None),
    ("pickle", THIS_DIR / "list_texts.pickle")
]


# -------------------- #
# -- WRITE AND READ -- #
# -------------------- #

@given(onelist = st.lists(st.text()))
def test_ioview_list_texts(onelist):
    for mode, path in MODES_PATHS:
        myioview = IOVIEW_CLASS(
            mode = mode,
            path = path
        )

        with myioview:
            for elt in onelist:
                myioview.write(elt)

            assert onelist == [elt for elt in myioview]

        myioview.remove()
