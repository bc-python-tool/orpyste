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
    """
    AST = ast.AST

    def build(self):
# We build the AST view.
        self.ast = self.AST(
            iotxt = self.iotxt,
            mode  = self.mode,
            store = self.store
        )

        self.ast.build()

# We can analyze and build our data object.
        self.incomment = False

        for metadata in self.ast:
            # print(metadata);continue
            kind = metadata['kind']

# A comment
            if kind.startswith("comment-"):
                if metadata['openclose'] == "open":
                    self.incomment = True
                    self.open_comment(kind[8:])

                else:
                    self.close_comment(kind[8:])

# A verbatim line (for comments indeed)
            elif kind == ":verbatim:":
                self.content_in_comment(metadata['content'])

# An empty line
            elif kind in ":emptyline:":
                if self.incomment:
                    self.emptyline_in_comment()

                else:
                    self.emptyline_content()

# A new block
            elif kind == "block":
                if metadata['openclose'] == "open":
                    self.incomment = False
                    self.open_block(metadata["groups_found"]["name"])

                    self.lastmode = metadata['mode']

                    if self.lastmode != "verbatim":
                        lastkeyval = {}
                        keysused   = []

                else:
                    self.close_block()

                    if self.lastmode != "verbatim" and lastkeyval:
                        self.addkeyval(lastkeyval)

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

                    key = content['key']

                    if self.lastmode == "keyval" and key in keysused:
                        raise PeufError(
                            "key already used, see line #{0}".format(
                                metadata['line']
                            )
                        )

                    keysused.append(key)

                    lastkeyval = content


# ------------------ #
# -- FOR COMMENTS -- #
# ------------------ #

    def open_comment(self, kind):
        ...

    def close_comment(self, kind):
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
