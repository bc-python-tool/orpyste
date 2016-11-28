#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import json

from mistool.os_use import PPath


# ------------------- #
# -- MODULE TESTED -- #
# ------------------- #

from orpyste.parse import walk


# ----------------------- #
# -- GENERAL CONSTANTS -- #
# ----------------------- #

THIS_DIR  = PPath(__file__).parent
DATAS_DIR = THIS_DIR / "datas_for_tests"


# -------------------------- #
# -- SUBCLASS FOR TESTING -- #
# -------------------------- #

class WALK_CLASS(walk.WalkInAST):
    def start(self):
        self.lines = ["START"]

    def end(self):
        self.lines.append("END")

    def open_comment(self, kind):
        self.lines.append("COMMENT-OPEN:{0}".format(kind))

    def close_comment(self, kind):
        self.lines.append("COMMENT-CLOSE:{0}".format(kind))

    def content_in_comment(self, line):
        self.lines.append("COMMENT-LINE:<<{0}>>".format(line))

    def open_block(self, name):
        self.lines.append("BLOCK-OPEN:{0}".format(name))

    def close_block(self, name):
        self.lines.append("BLOCK-CLOSE:{0}".format(name))

    def add_keyval(self, keyval):
        message = "KEYVAL:key=<<{0[key]}>> " \
                + "sep=<<{0[sep]}>> " \
                + "value=<<{0[value]}>>"

        self.lines.append(message.format(keyval))

    def add_line(self, line):
        self.lines.append("LINE:<<{0}>>".format(line))

    def add_magic_comment(self):
        self.lines.append("MAGIC-COMMENT")


# --------------- #
# -- CLEANINGS -- #
# --------------- #

def test_walk():
    for jsonpath in DATAS_DIR.walk("file::**.json"):
        with jsonpath.open() as f:
            mode = json.load(f)

        with jsonpath.with_ext("txt").open(
            encoding = "utf-8",
            mode     = "r"
        ) as f:
            output = f.read().strip()

        with WALK_CLASS(
            content = jsonpath.with_ext("peuf"),
            mode    = mode
        ) as walk_class:
            outputfound = "\n".join(walk_class.lines)

        assert output == outputfound
