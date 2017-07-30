#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import json

from mistool.os_use import PPath


# ------------------- #
# -- MODULE TESTED -- #
# ------------------- #

from orpyste import section


# ----------------------- #
# -- GENERAL CONSTANTS -- #
# ----------------------- #

THIS_DIR  = PPath(__file__).parent
DATAS_DIR = THIS_DIR / "datas_for_tests"

READBLOCK_SECTION_CLASS = section.ReadBlock
LOADJSON                = section.loadjson


# --------------- #
# -- CLEANINGS -- #
# --------------- #

def test_datablock_json():
    for jsonpath in DATAS_DIR.walk("file::read/**.json"):
        with jsonpath.open() as f:
            mode = json.load(f)

        with jsonpath.with_ext("txt").open(
            encoding = "utf-8",
            mode     = "r"
        ) as f:
            output = f.read().strip()

        with READBLOCK_SECTION_CLASS(
            content = jsonpath.with_ext("peuf"),
            mode    = mode
        ) as data_infos:
            dictversion = data_infos.flatdict

            jsonobj = data_infos.forjson

            assert dictversion == LOADJSON(jsonobj)
