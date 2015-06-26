#! /usr/bin/env python3

"""
prototype::
    date = 2015-06-????


????
"""

from orpyste.parse import ast


# ------------------------- #
# -- FOR ERRORS TO RAISE -- #
# ------------------------- #

class PeufError(ValueError):
    """
prototype::
    type = cls ;
           base class for errors specific to the peuf specifications.
    """
    pass


class WalkInAST():
    """
prototype::
    see = parse.ast.AST

    arg-attr = ??? ;
               ???

méthode communes au Redaer et au Clenaer !!!!

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

# We can analyze and build our data object.
        self.incomment = False
        self.kv_nbline = -1

        self.start()

        for metadata in self.ast:
            # print(metadata);continue
            self.kind   = metadata['kind']
            self.nbline = metadata['line']

# A comment
            if self.kind.startswith("comment-"):
                if metadata['openclose'] == "open":
                    self.incomment = True
                    self.open_comment()

                else:
                    self.incomment = False
                    self.close_comment()

# A verbatim line (for comments indeed)
            elif self.kind == ":verbatim:":
                self.content_in_comment(metadata['content'])

# An empty line
            elif self.kind == ":emptyline:":
                if self.incomment:
                    self.emptyline_in_comment()

                else:
                    self.emptyline_content()

# A new block
            elif self.kind == "block":
                if metadata['openclose'] == "open":
                    self.open_block(metadata["groups_found"]["name"])

                    self.lastmode = metadata['mode']

                    if self.lastmode != "verbatim":
                        lastkeyval = {}
                        keysused   = []

                else:
                    if self.lastmode != "verbatim" and lastkeyval:
                        self.addkeyval(lastkeyval)

# We have to take care of last comments in a block
                        self.kv_nbline = float("inf")
                        self.close_block()
                        self.kv_nbline = -1

                    else:
                        self.close_block()

            elif self.lastmode == "verbatim":
                self.addline(metadata['content']["value_in_line"])

            else:
                content = metadata['content']

                if "value_in_line" in content:
                    if not lastkeyval:
                        raise PeufError(
                            "missing first key, see line #{0}".format(
                                metadata['line']
                            )
                        )

                    lastkeyval['value'] += " " + content["value_in_line"].strip()

                else:
                    if lastkeyval:
                        self.addkeyval(lastkeyval)

                    self.kv_nbline = self.nbline
                    key            = content['key']

                    if self.lastmode == "keyval" and key in keysused:
                        raise PeufError(
                            "key already used, see line #{0}".format(
                                metadata['line']
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

    def emptyline_in_comment(self):
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


# ---------------- #
# -- EMPTY LINE -- #
# ---------------- #

    def emptyline_content(self):
        ...
