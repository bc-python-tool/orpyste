#! /usr/bin/env python3

"""
prototype::
    date = 2015-10-???


This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.
"""

from orpyste.tools.ioview import IOView
from orpyste.parse.walk import WalkInAST


# ------------- #
# -- READING -- #
# ------------- #

class Read(WalkInAST):
    """
prototype::
    see = parse.ast.AST , parse.walk.WalkInAST

    arg-attr = pathlib.Path, str: content ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str, dict: mode ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str: ??? = "" ;
               ???


===========
???
===========

???

prototype::


phase 1 on utilise IOView pour cérer une version

besoin d'autoriser plusieurs fois le même nom de bloc, avec par défaut un seul nom de bloc pour un contexte donné, concrètement meêm nom possible si sous bloc dans deux blocs parents différents

???
    """

# ------------------------------- #
# -- START AND END OF THE WALK -- #
# ------------------------------- #

    def start(self):
        self._verblines = []
        self._keyval    = []
        self._path      =[]

        print("START - self.walk_view.mode", self.walk_view.mode)

    def end(self):
        print("END - self._verblines", self._verblines)
        print("END - self._keyval", self._keyval)


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    def open_block(self, name):
        self._path.append(name)
        print("block\n    --->", name)
        print("self._path\n    --->", self._path)

    def close_block(self):
        self._path = []

        if self._verblines:
            print("line\n    --->", self._verblines)
            self._verblines = []

        elif self._keyval:
            print("keyval\n    --->", self._keyval)
            self._keyval = []


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    def add_keyval(self, keyval):
        self._keyval.append(keyval)


# -------------- #
# -- VERBATIM -- #
# -------------- #

    def add_line(self, line):
        if self.modes_stack and self.modes_stack[-1] == "verbatim":
            self._verblines.append(line)
