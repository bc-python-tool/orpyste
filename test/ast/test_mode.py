#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import json

from mistool.os_use import PPath


# ------------------- #
# -- MODULE TESTED -- #
# ------------------- #

from orpyste.parse import ast


# ----------------------- #
# -- GENERAL CONSTANTS -- #
# ----------------------- #

THIS_DIR  = PPath(__file__).parent
DATAS_DIR = THIS_DIR / "datas_for_tests"

MODE_CLASS = ast.Mode


# ----------- #
# -- TOOLS -- #
# ----------- #

def seps_in_sets(dicoview):
    if "seps" in dicoview:
        dicoview["seps"] = set(dicoview["seps"])


# ----------------- #
# -- SINGLE MODE -- #
# ----------------- #

def test_mode_alone():
    for jsonpath in DATAS_DIR.walk("file::mode/alone/*.json"):
        with jsonpath.open() as f:
            jsonobj = json.load(f)

        for mode, dicoview in jsonobj.items():
            dicoview_found = MODE_CLASS(mode = mode)[":default:"]

# Destroy sorting for separators.
        seps_in_sets(dicoview)
        seps_in_sets(dicoview_found)

        assert dicoview == dicoview_found


# ------------------ #
# -- SEVERAL MODE -- #
# ------------------ #

def test_multimode():
    for jsonpath in DATAS_DIR.walk("file::mode/multi/*.json"):
        with jsonpath.open() as f:
            jsonobj = json.load(f)

        mode_found = MODE_CLASS(mode = jsonobj["mode"])

        for blockname, dicoview in jsonobj["dicoview"].items():
            dicoview_found = mode_found[blockname]

# Destroy sorting for separators.
            if "seps" in dicoview:
                dicoview["seps"]       = set(dicoview["seps"])
                dicoview_found["seps"] = set(dicoview_found["seps"])

            assert dicoview == dicoview_found
