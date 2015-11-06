#! /usr/bin/env python3

"""
prototype::
    date = 2015-11-???


This module ????


allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.


"""

import re

from orpyste.tools.ioview import IOView
from orpyste.parse.walk import WalkInAST
from orpyste.parse.ast import LEGAL_BLOCK_NAME, \
                              CONTAINER, KEYVAL, MULTIKEYVAL, VERBATIM


# --------------------------------- #
# -- DECORATORS FOR THE LAZY MAN -- #
# --------------------------------- #

def canbeused(meth):
    """
property::
    see = Clean

    type = decorator

    arg = func: meth ;
          one method of the class ``Read``


????
    """
    def newmeth(self, *args, **kwargs):
        if not self.builddone:
            raise BufferError("the ``build`` method has not been called")

        return meth(self, *args, **kwargs)

    return newmeth


def adddata(meth):
    """
property::
    see = Clean

    type = decorator

    arg = func: meth ;
          one method of the class ``Read``


????
    """
    def newmeth(self, *args, **kwargs):
        self.walk_view.write({
            "mode": self.last_mode,
            "data": args[0]
        })

        return meth(self, *args, **kwargs)

    return newmeth



# ------------- #
# -- READING -- #
# ------------- #

OPEN, CLOSE = "open", "close"
DATAS_MODES = [KEYVAL, MULTIKEYVAL, VERBATIM]
NEWBLOCK    = "newblock"

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


phase 1 on utilise IOView pour cérer une version utilisant qpath pour q(uery) path

on ne garde que les données, donc les blicqs vides sont ignorés sans lever d'erreur ! en etre contient car lectrure = ecritue va effacer des choses (passer par clean de préréfence )

on obtient une version compact du fichier peuf stockable à long terme !


besoin d'autoriser plusieurs fois le même nom de bloc, avec par défaut un seul nom de bloc pour un contexte donné, concrètement meêm nom possible si sous bloc dans deux blocs parents différents

???
    """

# ------------------------------- #
# -- START AND END OF THE WALK -- #
# ------------------------------- #

    def start(self):
        self._verblines = []
        self._keyval    = []
        self._qpath     = []


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    def open_block(self, name):
        self._qpath.append(name)

        if self.last_mode in DATAS_MODES:
# Be aware of reference and list !
            self.walk_view.write({
                "qpath": "/".join(self._qpath),
                "mode" : self.last_mode
            })

    def close_block(self, name):
        self._qpath.pop(-1)


# ------------------------------------- #
# -- DATAS: (MULTI)KEYVAL & VERBATIM -- #
# ------------------------------------- #

    @adddata
    def add_keyval(self, keyval):
        ...

    @adddata
    def add_line(self, line):
        ...


# ----------------------------- #
# -- USER FRIENDLY ITERATORS -- #
# ----------------------------- #

    def __iter__(self):
        """
This a basic iterator that yiels the fllowing kind of dictuionaries ! see geitem car plus sympa !

{'qpath': ['main', 'test']}
{'data': {'key': 'aaa', 'sep': '=', 'value': '1 + 9 = 10'}, 'mode': 'keyval'}
{'data': {'key': 'bbbbbbbbb', 'sep': '<>', 'value': '2'}, 'mode': 'keyval'}
{'data': {'key': 'c', 'sep': '=', 'value': '3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and...'}, 'mode': 'keyval'}
{'qpath': ['main', 'sub_main', 'sub_sub_main', 'verb']}
{'data': '', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': 'line 1', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': '                line 2', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': '                                line 3', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
{'data': '', 'mode': 'verbatim'}
        """
        for infos in self.walk_view:
            yield infos


    def __getitem__(self, querypath):
        """
ceci est un iteratur en fait pour récupérer facilement des données  conjointement à KSVDict


block1/block2/block3 pour avoir la liste des lignes, ou bien celle des clés-valeurs ! Voir ia passage KSVDict


posibilité de regex comme */block3  (ajout automatique de ^ et $)
        """
# What has to be extracted ?
        query_pattern = re.compile("^{0}$".format(querypath))

# We can now extract the matching infos.
        datasfound = False
        newblock   = True

        for infos in self.walk_view:
            if "qpath" in infos:
                datasfound = query_pattern.search(infos["qpath"])

                if datasfound:
                    yield infos

            elif datasfound:
                yield _rtu_data(infos)


def _rtu_data(infos):
    """
rtu = ready to use
juste pour facilitéer le parcours pour clé séparateur valeur
    """
    if infos['mode'] == VERBATIM:
        return infos['data']

    else:
        data = infos['data']
        return data["key"], data["sep"], data["value"]
