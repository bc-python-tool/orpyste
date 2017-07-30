#! /usr/bin/env python3

"""
prototype::
    date = 2017-07-31


This module contains a class ``WalkInAST`` to be subclassed so as to walk in
the intermediate AST view made by the class ``parse.ast.AST``, and also to act
regarding the context or the data met during the walk.


info::
    The class ``WalkInAST`` do some semantic analysis that had not been done
    by the class ``parse.ast.AST``.
"""

from collections import Hashable, OrderedDict

from orpyste.parse.ast import *
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


# -------------------- #
# -- SAFE CONSTANTS -- #
# -------------------- #

KEYVAL_TAGS = KEY_TAG, SEP_TAG, VAL_TAG \
            = "key"  , "sep"  , "value"
VAL_IN_LINE_TAG = "value_in_line"


# -------------------------- #
# -- SPECIAL DICTIONARIES -- #
# -------------------------- #

# The following code of the class ``MKOrderedDict`` comes directly from the
# module ``mistool.python_use`` where it is maintained.

class MKOrderedDict():
    """
This class allows to work easily with multikeys ordered dictionaries. Here is
a complete example of use where some ouputs have been hand formatted.

pyterm::
    >>> from orpyste.parse.walk import MKOrderedDict
    >>> onemkdict = MKOrderedDict()
    >>> onemkdict[(1, 2, 4)] = "1st value"
    >>> onemkdict["key"] = "2nd value"
    >>> onemkdict["key"] = "3rd value"
    >>> print(onemkdict)
    MKOrderedDict([
        ((id=0, key=(1, 2, 4)), value='1st value'),
        ((id=0, key='key')    , value='2nd value'),
        ((id=1, key='key')    , value='3rd value')
    ])
    >>> for val in onemkdict["key"]:
    ...     print(k_id, val)
    ...
    0 2nd value
    1 3rd value
    >>> print(onemkdict.getitembyid(1, "key"))
    3rd value
    >>> for (k_id, key), val in onemkdict.items():
    ...     print((k_id, key), "===>", val)
    ...
    (0, (1, 2, 4)) ===> 1st value
    (0, 'key') ===> 2nd value
    (1, 'key') ===> 3rd value
    >>> for key, val in onemkdict.items(noid=True):
    ...     print(key, "===>", val)
    ...
    (1, 2, 4) ===> 1st value
    key ===> 2nd value
    key ===> 3rd value
    >>> "key" in onemkdict
    True
    >>> "kaaaay" in onemkdict
    False
    >>> onemkdict.setitembyid(0, "key", "New 2nd value")
    >>> print(onemkdict)
    MKOrderedDict([
        ((id=0, key=(1, 2, 4)), value='1st value'),
        ((id=0, key='key')    , value='New 2nd value'),
        ((id=1, key='key')    , value='3rd value')])
    """

    def __init__(self):
        self._internaldict = OrderedDict()
        self._keyids       = {}
        self._len          = 0

    def __setitem__(self, key, val):
        if not isinstance(key, Hashable):
            raise KeyError("key must be hashable")

        if key in self._keyids:
            self._keyids[key] += 1

        else:
            self._keyids[key] = 0

        self._internaldict[(self._keyids[key], key)] = val

        self._len += 1

    def setitembyid(self, keyid, key, val):
        if (keyid, key) not in self._internaldict:
            self._len += 1

        self._internaldict[(keyid, key)] = val

    def __getitem__(self, key, keyid = None):
        keyfound = False

        for (oneid, onekey), oneval in self._internaldict.items():
            if key == onekey:
                keyfound = True

                yield oneid, oneval

        if not keyfound:
            raise KeyError("key not used in the MKOrderedDict")

    def getitembyid(self, keyid, key):
        for (oneid, onekey), oneval in self._internaldict.items():
            if keyid == oneid and key == onekey:
                return oneval

        raise KeyError("key not used in the MKOrderedDict")

    def items(self, noid = False):
        for id_key, oneval in self._internaldict.items():
            if noid:
                yield id_key[1], oneval

            else:
                yield id_key, oneval

    def __contains__(self, key):
        for (oneid, onekey), oneval in self._internaldict.items():
            if key == onekey:
                return True

        return False

    def __len__(self):
        return self._len

    def __eq__(self, other):
        if not isinstance(other, MKOrderedDict):
            return False

        if self._internaldict.keys() != other._internaldict.keys():
            return False

        for k, v in self._internaldict.items():
            if v != other.getitembyid(*k):
                return False

        return True

    def __str__(self):
        text = repr(self)

        while "\n    " in text:
            text = text.replace("\n    ", "\n")

        text = text.replace("\n", "")

        return text

    def __repr__(self):
        text = ["MKOrderedDict(["]

        for (oneid, onekey), oneval in self._internaldict.items():
            text.append(
                "    (id={0}, key={1}, value={2}), ".format(
                    oneid,
                    repr(onekey),
                    repr(oneval).replace("\n    ", "\n        ")
                )
            )

        if len(text) != 1:
            text[-1] = text[-1][:-2]

        text.append("])")

        text = "\n".join(text)

        return text


# The following code of the class ``MKOrderedDict`` comes directly from the
# module ``mistool.python_use`` where it is maintained.

class RecuOrderedDict(OrderedDict):
    """
This subclass of ``collections.OrderedDict`` allows to use a list of hashable
keys, or just a single hashable key. Here is a complete example of use where
some ouputs have been hand formatted.

pyterm::
    >>> from orpyste.parse.walk import RecuOrderedDict
    >>> onerecudict = RecuOrderedDict()
    >>> onerecudict[[1, 2, 4]] = "1st value"
    >>> onerecudict[(1, 2, 4)] = "2nd value"
    >>> onerecudict["key"] = "3rd value"
    >>> print(onerecudict)
    RecuOrderedDict([
        (
            1,
            RecuOrderedDict([
                (
                    2,
                    RecuOrderedDict([ (4, '1st value') ])
                )
            ])
        ),
        (
            (1, 2, 4),
            '2nd value'
        ),
        (
            'key',
            '3rd value'
        )
    ])
    >>> [1, 2, 4] in onerecudict
    True
    >>> [2, 4] in onerecudict[1]
    True
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __getitem__(self, keys):
        if isinstance(keys, Hashable):
            return super().__getitem__(keys)

        else:
            first, *others = keys

            if others:
                return self[first][others]

            else:
                return self[first]


    def __setitem__(self, keys, val):
        if isinstance(keys, Hashable):
            super().__setitem__(keys, val)

        else:
            first, *others = keys

            if first in self and others:
                self[first][others] = val

            else:
                if others:
                    subdict         = RecuOrderedDict()
                    subdict[others] = val
                    val             = subdict

                self[first] = val


    def __contains__(self, keys):
        if isinstance(keys, Hashable):
            return super().__contains__(keys)

        else:
            first, *others = keys

            if first in self:
                if not others:
                    return True

                subdict = self[first]

                if isinstance(subdict, OrderedDict):
                    return others in subdict

            return False


# ----------------------------------- #
# -- DECORATOR(S) FOR THE LAZY MAN -- #
# ----------------------------------- #

def newcontent(meth):
    """
prototype::
    see = WalkInAST

    type = decorator

    arg = method: meth ;
          one method of the class ``WalkInAST``


This decorator "indicates" that something has been found.
    """
    def newmeth(self, *args, **kwargs):
        self._methodname = meth.__name__
        self.add_extra()

        return meth(self, *args, **kwargs)

    return newmeth


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
    arg-attr = str: encoding = "utf-8" ;
               see the documentation of ``parse.ast.AST``
    arg-attr = bool: build_asts = True ;
               **this variable is only useful for a content in a file.**
               ``build_asts = True`` indicates to analyse a file and to produce
               temporary files, whereas ``build_asts = False`` asks to use
               the temporary files (this is a way to store physically the
               partial analysis)
    arg-attr = bool: remove_asts = True ;
               **this variable is only useful for a content in a file.**
               ``remove_asts = True`` indicates to remove temporary files built
               to analyze a file, whereas ``remove_asts = False`` asks to keep
               the temporary files (this is a way to store physically the
               partial analysis)

    attr = orpyste.tools.ioview.IOView: walk_view ;
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
    informations and also the class ``orpyste.data.Read`` for one real example
    of use).

        * ``start`` and ``end`` are methods called just before and after the
        walk.

        * ``open_comment`` and ``close_comment`` are called when a comment has
        to be opened or closed, whereas ``content_in_comment`` allows to add a
        content met inside a comment.

        * ``open_section`` and ``close_section`` are called when a section has
        to be opened or closed, whereas ``section_title`` is for managing the
        title of section.

        * ``open_block`` and ``close_block`` are methods called just before and
        after a block is opened or closed respectively.

        * ``add_keyval`` can add a key-separator-value data.

        * ``add_line`` allows to add a single verbatim line.
    """
    AST = AST

    def __init__(
        self,
        content,
        mode,
        encoding    = "utf-8",
        build_asts  = True,
        remove_asts = True
    ):
        self.content  = content
        self.mode     = mode
        self.encoding = encoding

        self.build_asts  = build_asts
        self.remove_asts = remove_asts

        self.builddone = False

    def build(self):
# We build the AST view.
        self.ast = self.AST(
            mode    = self.mode,
            content = self.content
        )

        self.ast.build()

        if self.ast.view.mode == "list":
            self.walk_view = IOView(self.ast.view.mode)

        else:
            self.walk_view = IOView(
                mode = self.ast.view.mode,
                path = self.ast.view.datas.with_suffix(".walk")
            )

        with self.walk_view:
# -- START OF THE WALK -- #
            self.start()

# We must keep all metadatas for fine tuning in the attribut ``self.metadata``
# that contains all the necessary informations.
            self.datashasbeenfound = False
            self.isfirstsection   = True

            self.insection        = False
            self._section_title   = []

            self.incomment   = False
            self.indentlevel = -1

            self.last_mode   = ""
            self.modes_stack = []
            self.names_stack = []

            self.nb_empty_verbline = 0

            self.kv_nbline = -1
            lastkeyval     = {}

            for self.metadata in self.ast:
                # --- IMPORTANT : UGLY DEBUG --- #
                # print("--- @@@ WALK @@@ ---", self.metadata,sep="\n");continue

                kind = self.metadata[KIND_TAG]
                self.nbline = self.metadata[NBLINE_TAG]

# -- SECTION -- #
                if kind == "section":
                    if self.metadata[OPENCLOSE] == OPEN:
                        if self.isfirstsection \
                        and self.datashasbeenfound:
                            raise PeufError(
                                "datas found before the first section"
                            )

                        self.insection         = True
                        self.datashasbeenfound = True
                        self.isfirstsection    = False

                        self.open_section()

                    else:
                        titlesize = len(self._section_title)

                        if titlesize == 0:
                            raise PeufError(
                                "empty title for a section"
                            )

                        elif titlesize != 1:
                            raise PeufError(
                                "title for a section not upon a single line"
                            )

                        if "\\" in self._section_title[0] \
                        or "/" in self._section_title[0]:
                            raise PeufError(
                                "title can't contain << \ >> or << / >>"
                            )

                        self.section_title(self._section_title.pop(0))

                        self.insection = False
                        self.close_section()

# -- COMMENT -- #
                elif kind.startswith("comment-"):
                    if self.metadata[OPENCLOSE] == OPEN:
                        self.incomment = True

# Verbatim content is verbatim !!!!
                        if self.last_mode == VERBATIM:
                            self._add_empty_verbline()

                        self.open_comment(kind[8:])

                    else:
                        self.incomment = False
                        self.close_comment(kind[8:])

# -- COMMENT LINE OR TITLE OF A SECTION -- #
                elif kind == VERB_CONTENT_TAG:
                    if self.insection:
                        self._section_title.append(self.metadata[CONTENT_TAG])

                    else:
                        self.content_in_comment(self.metadata[CONTENT_TAG])

# -- EMPTY LINE -- #
                elif kind == EMPTYLINE_TAG:
                    if self.incomment:
                        self.content_in_comment("")

                    elif self.last_mode == VERBATIM:
                        self.nb_empty_verbline += 1

# -- BLOCK -- #
                elif kind == BLOCK_TAG:
# An opening block
                    if self.metadata[OPENCLOSE] == OPEN:
                        self.indentlevel += 1

                        self.last_mode = self.metadata[MODE_TAG]
                        self.modes_stack.append(self.last_mode)

                        name = self.metadata[GRPS_FOUND_TAG][NAME_TAG]
                        self.names_stack.append(name)

                        self.datashasbeenfound = True
                        self.open_block(name)

# For block with a content, we have to augment the value of the indentation.
                        if self.last_mode != CONTAINER:
                            self.indentlevel += 1

# We have to manage key-value modes fo which a value can be written over
# several lines !
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
                elif kind == MAGIC_COMMENT:
                    if self.last_mode != VERBATIM:
                        raise PeufError(
                            "magic comment not used for a verbatim content"
                        )

                    if self.metadata[OPENCLOSE] == OPEN:
                        self._add_empty_verbline()
                        self.add_magic_comment()

# -- VERBATIM CONTENT -- #   UTILE ??????
                elif self.last_mode == VERBATIM:
                    self._add_empty_verbline()
                    self.add_line(
                        self.metadata[CONTENT_TAG][VAL_IN_LINE_TAG]
                    )

# -- KEY-VAL CONTENT -- #
                else:
                    content = self.metadata[CONTENT_TAG]

                    if VAL_IN_LINE_TAG in content:
                        if not lastkeyval:
                            raise PeufError(
                                "missing first key, see line #{0}".format(
                                    self.metadata[NBLINE_TAG]
                                )
                            )

                        lastkeyval[VAL_TAG] \
                        += " " + content[VAL_IN_LINE_TAG].strip()
                        self.kv_nbline = self.metadata[NBLINE_TAG]

                    else:
                        if lastkeyval:
                            self.add_keyval(lastkeyval)

                        self.kv_nbline = self.metadata[NBLINE_TAG]
                        key            = content[KEY_TAG]

                        if self.last_mode == KEYVAL and key in keysused:
                            raise PeufError(
                                "key already used, see line #{0}".format(
                                    self.metadata[NBLINE_TAG]
                                )
                            )

                        keysused.append(key)

                        lastkeyval = content

# -- END OF THE WALK -- #

            self.end()

        self.builddone = True

        return self

# -- START AND END OF THE WALK -- #

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

    def remove_extras(self):
        self.ast.view.remove()
        self.walk_view.remove()

# -- COMMENTS -- #

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

# -- SECTIONS -- #

    def open_section(self):
        """
This method is for opening a section.
        """
        ...

    def close_section(self):
        """
This method is for closing a section.
        """
        ...

    def section_title(self, title):
        """
This method manages the title of a section.
        """
        ...

# -- BLOCKS -- #

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

# -- (MULTI)KEYVAL -- #

    def add_keyval(self, keyval):
        """
prototype::
    arg = {"key": str, "sep": str, "value": str}: keyval


This method is for adding a new key with its associated value and separator.
All this informations are in the dictionary ``keyval``.
        """
        ...

# -- VERBATIM -- #

# We have to take care of the last empty lines !!!
    def _add_empty_verbline(self):
        if self.nb_empty_verbline:
            self.nbline -= self.nb_empty_verbline + 1

            for _ in range(self.nb_empty_verbline):
                self.nbline += 1
                self.add_line("")

            self.nbline += 1
            self.nb_empty_verbline = 0

    def add_line(self, line):
        """
prototype::
    arg = str: line


This method is for adding verbatim content.
        """
        ...

    def add_magic_comment(self):
        """
This method is for adding the magic comment used for empty lines at the end of
verbatim contents.
        """
        ...

# -- CONTEXT MANAGER -- #

    def __enter__(self):
# We have to always build asts if the content is a string !
        if self.build_asts \
        or not isinstance(self.content, str):
            self.build()

        return self

    def __exit__(self, type, value, traceback):
        if self.remove_asts:
            self.remove_extras()
