#! /usr/bin/env python3

"""
prototype::
    date = 2015-11-16


This module contains a class ``WalkInAST`` to be subclassed so as to walk in the
intermediate AST view made by the class ``parse.ast.AST``, and alsa so as to
act regarding the context or the data met during the walk.


info::
    The class ``WalkInAST`` do some semantic analysis that have not been done by
    the class ``parse.ast.AST``.
"""

from orpyste.parse.ast import(
    AST,
    CONTAINER,
    KEYVAL,
    MULTIKEYVAL,
    VERBATIM
)
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


# ------------- #
# -- WALKING -- #
# ------------- #

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
    attr = str: last_mode ;
           this string is the mode of the very last block opened 
    attr = list: modes_stack ;
           this stack list contains the modes of the last blocks opened 
    attr = dict: metadata ;
           this is a dictionary sent when using ``for metadata in oneast: ...``
           where ``oneast`` is an instance of ``parse.ast.AST``. This gives you
           all informations about the current piece of the AST.


warning::
    This class only implements the walking but she doesn't acheive any action.
    To do something, you have to subclass ``WalkInAST`` and to implement what
    you need in the following methods (see their documentations for more
    informations and also the class ``orpyste.data.Read`` for one example of
    use).

        * ``start`` and ``end`` are methods called just before and after the
        walk.
        * ``open_comment`` and ``close_comment`` are called when a comment has
        to be opened or closed, whereas ``content_in_comment`` allows to add a
        content met inside a comment.
        * ``open_block`` and ``close_block`` are methods called just before and
        after a block is opened or closed respectively.
        * ``add_keyval`` can add a key-separator-value data.
        * ``add_line`` allows to add a single verbatim line.
    """
    AST = AST

    def __init__(
        self,
        content,
        mode
    ):
        self.content = content
        self.mode    = mode

        self.builddone = False


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

            self.last_mode   = ""
            self.modes_stack = []
            self.names_stack = []

            self.nb_empty_verbline = 0

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

                    elif self.last_mode == VERBATIM:
                        self.nb_empty_verbline += 1

# -- BLOCK -- #
                elif kind == "block":
# An opening block
                    if self.metadata['openclose'] == "open":
                        self.indentlevel += 1

                        self.last_mode = self.metadata['mode']
                        self.modes_stack.append(self.last_mode)

                        name = self.metadata["groups_found"]["name"]
                        self.names_stack.append(name)
                        self.open_block(name)

# For block with a content, we have to augment the value of the indentation.
                        if self.last_mode != CONTAINER:
                            self.indentlevel += 1

# We have to manage key-value modes fo which a value can be written over several
# lines !
                        if self.last_mode.endswith(KEYVAL):
                            lastkeyval = {}
                            keysused   = []

# A closing block
                    else:
                        if self.last_mode == VERBATIM:
                            self.nb_empty_verbline = 0

                        name = self.names_stack.pop(-1)

# Do we have a key-value couple ?
                        if lastkeyval:
                            self.add_keyval(lastkeyval)
                            lastkeyval = {}
                            keysused   = []
                            self.indentlevel -= 1

# We have to take care of last comments in a block
                            self.kv_nbline = float("inf")
                            self.close_block(name)
                            self.kv_nbline = -1

                        else:
# Are we closing a block with a content ?
                            if self.last_mode != CONTAINER:
                                self.indentlevel -= 1

                            self.close_block(name)

                        self.indentlevel -= 1
                        self.modes_stack.pop(-1)

                        if self.modes_stack:
                            self.last_mode = self.modes_stack[-1]
                        else:
                            self.last_mode = ""


# -- MAGIC COMMENT -- #
                elif kind == "magic-comment":
                    if self.last_mode != VERBATIM:
                        raise PeufError(
                            "magic comment not used for a verbatim content"
                        )

                    if self.metadata['openclose'] == "open":
                        self._add_empty_verbline()
                        self.add_magic_comment()


# -- VERBATIM CONTENT -- #
                elif self.last_mode == VERBATIM:
                    self._add_empty_verbline()
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

                        if self.last_mode == KEYVAL and key in keysused:
                            raise PeufError(
                                "key already used, see line #{0}".format(
                                    self.metadata['line']
                                )
                            )

                        keysused.append(key)

                        lastkeyval = content


# -- END OF THE WALK -- #
            self.end()

        self.builddone = True

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
          which is all in a single line


This method is for opening a comment. No content is given there (see the method
``content_in_comment``).
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
          which is all in a single line


This method is for closing a comment. No content is given there (see the method
``content_in_comment``).
        """
        ...

    def content_in_comment(self, line):
        """
prototype::
    arg = str: line


This method is for adding content inside a comment (see the methods
``open_comment`` and ``close_comment``).
        """
        ...


# ------------ #
# -- BLOCKS -- #
# ------------ #

    def open_block(self, name):
        """
prototype::
    arg = str: name


This method is for opening a new block knowning its name.
        """
        ...

    def close_block(self, name):
        """
This method is for closing a block knowning its name.
        """
        ...


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    def add_keyval(self, keyval):
        """
prototype::
    arg = {"key": str, "sep": str, "value": str}: keyval


This method is for adding a new key with its associated value and separator. All
this informations are in the dictionary ``keyval``.
        """
        ...


# -------------- #
# -- VERBATIM -- #
# -------------- #

    def _add_empty_verbline(self):
        for _ in range(self.nb_empty_verbline):
            self.add_line("")

        self.nb_empty_verbline = 0


    def add_magic_comment(self):
        """
This method is for adding the magic comment used for empty lines at the end of
verbatim contents.
        """
        ...


    def add_line(self, line):
        """
prototype::
    arg = str: line


This method is for adding verbatim content.
        """
        ...
