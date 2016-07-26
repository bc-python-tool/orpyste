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


# --------------- #
# -- CLEANINGS -- #
# --------------- #

def test_datablock_search_nblineof():
    for jsonpath in DATAS_DIR.walk("file::search/**.json"):
        with jsonpath.open() as f:
            jsonobj = json.load(f)

        mode   = jsonobj["mode"]
        search = jsonobj["search"]

        data_infos = READBLOCK_CLASS(
            content = jsonpath.with_ext("peuf"),
            mode    = mode
        )

        data_infos.build()

        for querypath, nblineof in search.items():
            assert nblineof == data_infos.nblineof(querypath)

        data_infos.remove()
