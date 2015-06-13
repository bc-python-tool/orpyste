#! /usr/bin/env python3

"""
prototype::
    date = 2015-????


This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.
"""

from orpyste.parse import ast, pyit


class Read():
    """
prototype::
    see = parse.ast , parse.pyit

    arg = file, io.StringIO: iotxt ;
          ???
          either  f = open("myfile.txt", "r", encoding="utf-8")
          In-memory text streams are also available as StringIO objects:
          or
          f = io.StringIO("some initial text data")
    arg = str: mode = "equal" ;
          ???
    arg = str: seps = "=" ;
          ???


???
    """

    AST  = ast.AST
    PYIT = pyit.AST2PY


    def __init__(
        self,
        iotxt,
        mode = "equal",
        seps = "=",
    ):
# Public attributs
        self.iotxt = iotxt
        self.mode  = mode
        self.seps  = seps


# --------------------- #
# -- BUILD THE DATAS -- #
# --------------------- #

    def build(self):
# We build the AST view.
        _AST = self.AST(
            iotxt = self.iotxt,
            mode  = self.mode,
            seps  = self.seps
        )

        _AST.build()


# Transforming the AST view to a more friendly format.
