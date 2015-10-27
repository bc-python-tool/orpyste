#! /usr/bin/env python3

"""
prototype::
    date = 2015-07-07     DOCSTRING ---> À finir !!!!


This module gives methods to walk in the intermediate AST view made by the class
``parse.ast.AST``.


info::
    Here we do some semantic analysis that have not been done by the class
    ``parse.ast.AST``.
"""

from orpyste.parse import ast
from orpyste.tools.ioview import IOView


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

    arg-attr = pathlib.Path, str: content ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str, dict: mode ;
               see the documentation of ``parse.ast.AST``

    attr = orpyste.tools.ioview.IOView: self.walk_view ;
           this is the attribut to use if you want to store information during
           the walk.
    attr = dict: metadata ;
           this is a dictionary sent when using ``for metadata in oneast: ...``
           where ``oneast`` is an instance of ``parse.ast.AST``. This gives you
           all informations about the current piece of the AST.
    attr = list: modes_stack ;
           this stack list contains the modes of the last blocks opened 


warning::
    This class only implements the walking but she doesn't do any action. To do
    that, you have to subclass ``WalkInAST`` and to implement what you need in
    the following methods.

        * ``start``
        * ``end``
        * ``open_comment``
        * ``close_comment``
        * ``content_in_comment``
        * ``open_block``
        * ``close_block``
        * ``add_keyval``
        * ``add_line``
    """
    AST = ast.AST

    def __init__(
        self,
        content,
        mode
    ):
        self.content = content
        self.mode    = mode


    def build(self):
# We build the AST view.
        self.ast = self.AST(
            content = self.content,
            mode    = self.mode
        )

        self.ast.build()

        self.walk_view = IOView(self.ast.view.mode)

        with self.walk_view:
# -- START OF THE WALK -- #
            self.start()

# We must keep all metadatas for fine tuning in the attribut ``self.metadata``
# that contains all the necessary informations.
            self.incomment   = False
            self.indentlevel = -1
            self.modes_stack = []

            self.kv_nbline = -1
            lastkeyval     = {}

            for self.metadata in self.ast:
                kind = self.metadata['kind']


# -- COMMENT -- #
                if kind.startswith("comment-"):
                    if self.metadata['openclose'] == "open":
                        self.incomment = True
                        self.open_comment(kind[8:])

                    else:
                        self.incomment = False
                        self.close_comment(kind[8:])


# -- COMMENT LINE -- #
                elif kind == ":verbatim:":
                    self.content_in_comment(self.metadata['content'])


# -- EMPTY LINE -- #
                elif kind == ":emptyline:":
                    if self.incomment:
                        self.content_in_comment("")

                    else:
                        self.add_line("")


# -- BLOCK -- #
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
                            self.add_keyval(lastkeyval)
                            lastkeyval = {}
                            keysused   = []
                            self.indentlevel -= 1

# We have to take care of last comments in a block
                            self.kv_nbline = float("inf")
                            self.close_block()
                            self.kv_nbline = -1

                        else:
# Are we closing a block with a content ?
                            if self.modes_stack[-1] != "container":
                                self.indentlevel -= 1

                            self.close_block()

                        self.indentlevel -= 1
                        self.modes_stack.pop(-1)


# -- VERBATIM CONTENT -- #
                elif self.modes_stack[-1] == "verbatim":
                    self.add_line(self.metadata['content']["value_in_line"])


# -- KEY-VAL CONTENT -- #
                else:
                    content = self.metadata['content']

                    if "value_in_line" in content:
                        if not lastkeyval:
                            raise PeufError(
                                "missing first key, see line #{0}".format(
                                    self.metadata['line']
                                )
                            )

                        lastkeyval['value'] \
                        += " " + content["value_in_line"].strip()

                    else:
                        if lastkeyval:
                            self.add_keyval(lastkeyval)

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


# -- END OF THE WALK -- #
            self.end()


# ------------------------------- #
# -- START AND END OF THE WALK -- #
# ------------------------------- #

    def start(self):
        """
This method is called just before the walk starts.
        """
        ...

    def end(self):
        """
This method is called just after the end of the walk.
        """
        ...


# -------------- #
# -- COMMENTS -- #
# -------------- #

    def open_comment(self, kind):
        """
prototype::
    arg = str: kind in ["singleline", "multilines", "multilines-singleline"] ;
          ``kind = "singleline"`` is for orpyste::``// ...``,
          ``kind = "multilines"`` is for orpyste::``/* ... */`` where the
          content contains at least one back return, and
          ``kind = "multilines-singleline"`` is for orpyste::``/* ... */``
          which is all in one line


This method is for opening a comment. No content is given there.
        """
        ...

    def close_comment(self, kind):
        """
prototype::
    arg = str: kind in ["singleline", "multilines", "multilines-singleline"] ;
          ``kind = "singleline"`` is for orpyste::``// ...``,
          ``kind = "multilines"`` is for orpyste::``/* ... */`` where the
          content contains at least one back return, and
          ``kind = "multilines-singleline"`` is for orpyste::``/* ... */``
          which is all in one line


This method is for closing a comment. No content is given there.
        """
        ...

    def content_in_comment(self, line):
        """
prototype::
    arg = str: line


This method is for adding content in a comment.
        """
        ...


# ------------ #
# -- BLOCKS -- #
# ------------ #

    def open_block(self, name):
        """
prototype::
    arg = str: name


This method is for opening a new block knowing its name.
        """
        ...

    def close_block(self):
        """
This method is for closing a block. No name is given there.
        """
        ...


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    def add_keyval(self, keyval):
        """
prototype::
    arg = {str: str}: keyval ;
          this dictionary looks like ``{"key": ..., "sep": ..., "value": ...}``.


This method is for adding a new key with its associated value and the separator
used. All this informations are in the dictionary ``keyval``.
        """
        ...


# -------------- #
# -- VERBATIM -- #
# -------------- #

    def add_line(self, line):
        """
prototype::
    arg = str: line


This method is for adding content.
        """
        ...
