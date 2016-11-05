#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import json

from mistool.os_use import PPath


# ------------------- #
# -- MODULE TESTED -- #
# ------------------- #

from orpyste import data


# ----------------------- #
# -- GENERAL CONSTANTS -- #
# ----------------------- #

THIS_DIR  = PPath(__file__).parent
DATAS_DIR = THIS_DIR / "datas_for_tests"

READBLOCK_CLASS = data.ReadBlock
LOADJSON        = data.loadjson


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

        data_infos = READBLOCK_CLASS(
            content = jsonpath.with_ext("peuf"),
            mode    = mode
        )

        data_infos.build()

        for kind in ["f", "r"]:
            for nosep in [True, False]:
                if kind == "r":
                    dictversion = data_infos.recudict(nosep = nosep)

                else:
                    dictversion = data_infos.flatdict(nosep = nosep)

                jsonobj = data_infos.jsonify(kind = kind, nosep = nosep)

                assert dictversion == LOADJSON(jsonobj)

        data_infos.remove()
