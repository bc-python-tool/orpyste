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

AST_CLASS = ast.AST


# --------------- #
# -- METADATAS -- #
# --------------- #

def test_ast_metadatas():
    for jsonpath in DATAS_DIR.walk("file::ast/*.json"):
        with jsonpath.open() as f:
            jsonobj = json.load(f)

        ast = AST_CLASS(
            content = "\n".join(jsonobj["lines"]),
            mode    = jsonobj["mode"]
        )

        ast.build()

        assert jsonobj["metadatas"] == [metadata for metadata in ast]
