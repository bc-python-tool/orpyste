#! /usr/bin/env python3

"""
Directory : orpyste
Name      : data
Version   : 2014.10
Author    : Christophe BAL
Mail      : projetmbc@gmail.com

This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.


système un peu fin
    --> l-gne vide qui se suive réuni sausf si ....
    --> gestion séparé du nettoyage hors commentaire ou dans commentaire
    --> pour le reste on garde un truc normatif malgré tout
"""

from orpyste.parse import ast, walk


# ------------- #
# -- READING -- #
# ------------- #

class Clean(walk.WalkInAST):
    """
    """

    COMMENT_DECO = {
        "open": {
            "singleline": "//",
            "multilines": "/*"
        },
        "close": {
            "singleline": "",
            "multilines": "*/"
        },
    }


    def __init__(
        self,
        iotxt,
        mode  = "keyval::=",
        store = "memory"
    ):
# Public attributs
        self.iotxt = iotxt
        self.mode  = mode
        self.store = store

# Internal attribut
        self._comment = []


# ------------------ #
# -- FOR COMMENTS -- #
# ------------------ #

    def open_comment(self, kind):
        if kind.startswith("multilines"):
            kind = "multilines"

        self._comment.append(self.COMMENT_DECO["open"][kind])

    def close_comment(self, kind):
        if kind.startswith("multilines"):
            kind = "multilines"

        self._comment.append(self.COMMENT_DECO["close"][kind])
        print(" ".join(self._comment))
        self._comment = []

    def emptyline_in_comment(self):
        self._comment.append('')

    def content_in_comment(self, line):
        self._comment.append(line)


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    def open_block(self, name):
        print("{0}".format(name))

    def close_block(self):
        print('\n')


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    def addkeyval(self, keyval):
        print("{0[key]} {0[sep]} {0[value]}".format(keyval))


# -------------- #
# -- VERBATIM -- #
# -------------- #

    def addline(self, line):
        print("    ", line)


# ---------------- #
# -- EMPTY LINE -- #
# ---------------- #

    def emptyline_content(self):
        print('')
