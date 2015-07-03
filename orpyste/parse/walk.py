#! /usr/bin/env python3

"""
prototype::
    date = 2015-07-03


This module gives methods to walk in the intermedaite AST view made by the class
``parse.ast.AST``.


info::
    Here we do semantic analysis that have not been done by the class
    ``parse.ast.AST``.
"""

from orpyste.parse import ast


# ------------------------- #
# -- FOR ERRORS TO RAISE -- #
# ------------------------- #

class PeufError(ValueError):
    """
prototype::
    type = cls ;
           base class for errors specific to the ¨peuf specifications.
    """
    pass


class WalkInAST():
    """
prototype::
    see = parse.ast.AST

    attr = ??? ;
           ???

méthode communes au Redaer et au Clenaer !!!!

self.metadata  contient info du moment !!!!

self.modes_stack


methode non implemnte comme cela on implémente juste ce dont on a besoin (pour data on se fuchie lihne vide et cilmentaire)
    """
    AST = ast.AST

    def build(self):
# We build the AST view.
        self.ast = self.AST(
            content = self.content,
            mode    = self.mode
        )

        self.ast.build()

# We have to use the start method of the subclass.
        self.start()

# We keep all metadatas for fine tuning in the attribut ``self.metadata`` that
# contains all the necessary informations.
        self.incomment   = False
        self.indentlevel = -1
        self.modes_stack = []

        self.kv_nbline = -1
        lastkeyval     = {}

        for self.metadata in self.ast:
            # print(self.metadata);continue
            kind = self.metadata['kind']

# -- A comment to open or close -- #
            if kind.startswith("comment-"):
                if self.metadata['openclose'] == "open":
                    self.incomment = True
                    self.open_comment()

                else:
                    self.incomment = False
                    self.close_comment()

# -- A comment line -- #
            elif kind == ":verbatim:":
                self.content_in_comment(self.metadata['content'])

# -- An empty line -- #
            elif kind == ":emptyline:":
                self.addline("")

# -- A new block -- #
            elif kind == "block":
# An opening block
                if self.metadata['openclose'] == "open":
                    self.indentlevel += 1

                    lastmode = self.metadata['mode']
                    self.modes_stack.append(lastmode)

                    self.open_block(self.metadata["groups_found"]["name"])

# For block with a content, we have to augment the value of the indentation.
                    if lastmode != "container":
                        self.indentlevel += 1

# We have to manage key-value modes fo which a value can be written over several
# lines !
                    if lastmode.endswith("keyval"):
                        lastkeyval = {}
                        keysused   = []

# A closing block
                else:
# Do we have a key-value couple ?
                    if lastkeyval:
                        self.addkeyval(lastkeyval)
                        lastkeyval = {}
                        keysused   = []
                        self.indentlevel -= 1

# We have to take care of last comments in a block
                        self.kv_nbline = float("inf")
                        self.close_block()
                        self.kv_nbline    = -1

                    else:
# Are we closing a block with a content ?
                        if self.modes_stack[-1] != "container":
                            self.indentlevel -= 1

                        self.close_block()

                    self.indentlevel -= 1
                    self.modes_stack.pop(-1)

# -- A verbatim content -- #
            elif self.modes_stack[-1] == "verbatim":
                self.addline(self.metadata['content']["value_in_line"])

# -- A key-val content -- #
            else:
                content = self.metadata['content']

                if "value_in_line" in content:
                    if not lastkeyval:
                        raise PeufError(
                            "missing first key, see line #{0}".format(
                                self.metadata['line']
                            )
                        )

                    lastkeyval['value'] += " " + content["value_in_line"].strip()

                else:
                    if lastkeyval:
                        self.addkeyval(lastkeyval)

                    self.kv_nbline = self.metadata["line"]
                    key            = content['key']

                    if self.modes_stack[-1] == "keyval" and key in keysused:
                        raise PeufError(
                            "key already used, see line #{0}".format(
                                self.metadata['line']
                            )
                        )

                    keysused.append(key)

                    lastkeyval = content

        self.end()


# --------------------------- #
# -- START AND END OF FILE -- #
# --------------------------- #

    def start(self):
        ...

    def end(self):
        ...


# ------------------ #
# -- FOR COMMENTS -- #
# ------------------ #

    def open_comment(self):
        ...

    def close_comment(self):
        ...

    def content_in_comment(self, line):
        ...


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    def open_block(self, name):
        ...

    def close_block(self):
        ...


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    def addkeyval(self, keyval):
        ...


# -------------- #
# -- VERBATIM -- #
# -------------- #

    def addline(self, line):
        ...
