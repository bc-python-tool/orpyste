#! /usr/bin/env python3

"""
prototype::
    date = 2015-06-21


This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.
"""

from orpyste.parse import walk


# ------------- #
# -- READING -- #
# ------------- #

class Read(walk.WalkInAST):
    """
prototype::
    arg = file, io.StringIO: content ;
          ???
          either  f = open("myfile.txt", "r", encoding="utf-8")
          In-memory text streams are also available as StringIO objects:
          or
          f = io.StringIO("some initial text data")

    arg = passer par une classe via un mode simple de config
        : config ;
        str: mode = "keyval::=" with {keyval} in self.IN_CTXTS
                                                or in self.LONG_IN_CTXTS ;

          si string c'est que pour des blocs de niveau 1 tus du même type


          keyval        onekey=...
          multikeyval   multikey=...
          line          line by line content
          verbatim      single verbaitm string !!!!

          = ou plusieurs opérateurs sans esapce commme dans
          multikeyval:: = < >

          espace de début pour lisibiliré uniquement


          dict comme avant toujours possible car pratqiue au jour le jour

          config via classe dédié pour cas complexe ou typage des données si besoin`

          Z !!!! Par contre on doit passer par classe dédiée qu el'on met en fait ici



    arg = str: store = "memory" in self.STORING_MODES
                              or in self.LONG_STORING_MODES ;



besoin d'autoriser plusieurs fois le même nom de bloc, avec par défaut un seul nom de bloc pour un contexte donné, concrètement meêm nom possible si sous bloc dans deux blocs parents différents

???
    """

    def __init__(
        self,
        content,
        mode  = "keyval::="
    ):
# Public attributs
        self.content = content
        self.mode    = mode


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    def open_block(self, name):
        print("{0}::".format(name))


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    def addkeyval(self, keyval):
        print("    --->", keyval)


# -------------- #
# -- VERBATIM -- #
# -------------- #

    def addline(self, line):
        print("    --->", line)
