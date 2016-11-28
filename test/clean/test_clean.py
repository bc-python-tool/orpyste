#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import json

from mistool.os_use import PPath


# ------------------- #
# -- MODULE TESTED -- #
# ------------------- #

from orpyste import clean


# ----------------------- #
# -- GENERAL CONSTANTS -- #
# ----------------------- #

THIS_DIR  = PPath(__file__).parent
DATAS_DIR = THIS_DIR / "datas_for_tests"

CLEAN_CLASS = clean.Clean


# --------------- #
# -- CLEANINGS -- #
# --------------- #

def test_clean():
    for jsonpath in DATAS_DIR.walk("file::**.json"):
        with jsonpath.open() as f:
            jsonobj = json.load(f)

        layout = jsonobj.get("layout", "")
        mode   = jsonobj["mode"]

        with CLEAN_CLASS(
            content = jsonpath.with_ext("peuf"),
            layout  = layout,
            mode    = mode
        ) as cleaned_infos:
# Comments are sent into a single piece of lines with necessary back returns  !
            cleaned_lines_found = "\n".join(line for line in cleaned_infos.view)
            cleaned_lines_found = [
                "file tested >>> {0}".format(jsonpath.stem)
            ] + cleaned_lines_found.split("\n")

        path_cleaned_text_wanted = DATAS_DIR / jsonpath.with_ext("txt")
        cleaned_lines_wanted     = [cleaned_lines_found[0]]

        with path_cleaned_text_wanted.open(
            encoding = "utf-8",
            mode     = "r"
        ) as f:
            cleaned_lines_wanted += [line.rstrip() for line in f.readlines()]
            cleaned_lines_wanted += [''] # Last empty decorating line !

        assert cleaned_lines_wanted == cleaned_lines_found
