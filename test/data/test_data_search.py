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

READ_SECTION_CLASS = section.Read


# --------------- #
# -- CLEANINGS -- #
# --------------- #

def test_data_read_all():
    for jsonpath in DATAS_DIR.walk("file::search/**.json"):
        with jsonpath.open() as f:
            jsoninfos = json.load(f)

        mode   = jsoninfos["mode"]
        search = jsoninfos["search"]

        with READ_SECTION_CLASS(
            content = jsonpath.with_ext("peuf"),
            mode    = mode
        ) as data_infos:
            for querypath, nblines in search.items():
                nblinesfound = []

                for oneinfo in data_infos[querypath]:
                    if oneinfo.isblock():
                        nblinesfound.append(oneinfo.nbline)

                print(jsonpath, "--->", querypath, ":", nblinesfound)

                assert nblines == nblinesfound
