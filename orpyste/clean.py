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


# -------------------------------- #
# -- DECORATOR FOR THE LAZY MAN -- #
# -------------------------------- #

def closecomments(meth):
    def newmeth(inst, *args, **kwargs):
        while(
            inst._comment
            and
            (
                inst.lastmode == "verbatim"
                or
                inst.kv_nbline > inst._comment[0]['nbline']
            )
        ):
            kind = inst._comment[0]['kind']

            if kind.startswith('multilines'):
                kind = 'multilines'

            inst._remove_empty(-1)

            if not inst._blockisempty:
                inst._text.append("")

            inst._text.append(
                "{0}{1}{2}".format(
                    inst.COMMENT_DECO['open'][kind],
                    "\n".join(inst._comment.pop(0)['content']),
                    inst.COMMENT_DECO['close'][kind]
                )
            )

        return meth(inst, *args, **kwargs)

    return newmeth


# -------------- #
# -- CLEANING -- #
# -------------- #

class Clean(walk.WalkInAST):
    """

on doit stocker commentaire, ligne vide seule, ainis que leur position pour bien placer lors d'un nouveau bloc, ou bien face a cle valeur sur plusieurs lignes !!!
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
        content,
        mode  = "keyval::="
    ):
# Public attributs
        self.content = content
        self.mode    = mode


    def _remove_empty(self, i):
        while(
            self._text
            and
            self._text[i] == ''
        ):
            self._text.pop(i)

    def addindentation(self, text):
        return "{0}{1}".format(
            " "*4*self.indentlevel,
            text
        )


# --------------------------- #
# -- START AND END OF FILE -- #
# --------------------------- #

    def start(self):
        self._comment = []
        self._text    = []

    def end(self):
# We clean empty lines at the begining and the end of the content.
        for i in [0, -1]:
            self._remove_empty(i)

        print("\n".join(self._text))


# ------------------ #
# -- FOR COMMENTS -- #
# ------------------ #

    def open_comment(self):
        self._comment.append({
            "nbline" : self.nbline,
            "kind"   : self.kind[8:],
            "content": []
        })

    def emptyline_in_comment(self):
        self._comment[-1]["content"].append('')

    def content_in_comment(self, line):
        self._comment[-1]["content"].append(line)


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    @closecomments
    def open_block(self, name):
        self._blockisempty = True
        self._text.append(
            "{0}::".format(self.addindentation(name))
        )

    @closecomments
    def close_block(self):
        self._remove_empty(-1)
        self._text += ['', '']


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    @closecomments
    def addkeyval(self, keyval):
        if self._blockisempty == True:
            self._blockisempty = False

        key = keyval["key"]
        sep = keyval["sep"]
        val = keyval["value"]

        self._text.append(
            "    {0} {1} {2}".format(
                self.addindentation(key),
                sep,
                val
            )
        )

# -------------- #
# -- VERBATIM -- #
# -------------- #

    @closecomments
    def addline(self, line):
        if self._blockisempty == True:
            self._blockisempty = False

        self._text.append(self.addindentation(line))


# ---------------- #
# -- EMPTY LINE -- #
# ---------------- #

    @closecomments
    def emptyline_content(self):
        if not (
            self._blockisempty
            or
            self.lastmode.endswith('keyval')
        ):
            self._text.append('')
