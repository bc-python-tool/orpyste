#! /usr/bin/env python3

"""
prototype::
    date = 2015-11-06


This module is for reading and extractings easily ¨infos in ¨peuf files.
"""

import re

from orpyste.parse.ast import (
    CONTAINER,
    KEYVAL,
    LEGAL_BLOCK_NAME,
    MULTIKEYVAL,
    VERBATIM
)
from orpyste.parse.walk import WalkInAST
from orpyste.tools.ioview import IOView


# ----------------------------------- #
# -- DECORATOR(S) FOR THE LAZY MAN -- #
# ----------------------------------- #

def adddata(meth):
    """
property::
    see = Read

    type = decorator

    arg = func: meth ;
          one method of the class ``Read``


This decorator is used each time that a new data has to be stored.
    """
    def newmeth(self, *args, **kwargs):
        self.walk_view.write(
            Infos(
                data = args[0],
                mode = self.last_mode
            )
        )

        return meth(self, *args, **kwargs)

    return newmeth


# ----------- #
# -- INFOS -- #
# ----------- #

class Infos():
    """
prototype::
    see = Read

    arg-attr = None , str: querypath = None ;
               a file like path used to walk in datas using ¨python regexes
               without opening ``^`` and closing ``$``
    arg-attr = None , str: mode = None ;
               the mode of a block or a data
    arg-attr = None , str , {'sep': str, 'key': str, 'value': str}: data = None ;
               the datas found if the mode is for one data


Here are some examples.

    * ``mode = "keyval"`` and ``querypath = "main/test"``.
    * ``mode = "keyval"`` and ``data = {'sep = '=', 'key = 'a', 'value = '1'}``.
    * ``mode = "verbatim"`` and ''querypath = "main/sub_main/verb"''.
    * ``mode = "verbatim"`` and ``data = ""``.
    * ``mode = "verbatim"`` and ``data = "One line..."``.
    * ... ¨etc.
    """

    _KEYSEPVAL = ["key", "sep", "value"]

    def __init__(
        self,
        querypath = None,
        mode      = None,
        data      = None
    ):
        self.querypath = querypath
        self.mode      = mode
        self.data      = data


    @property
    def isnewblock(self):
        return self.querypath != None


    @property
    def rtu_data(self):
        """
prototype::
    return = str , [str, str, str] ;
             if we have one data, for a verbatim content the actual line is
             returned, and for a key-value content that is a list looking like
             ``[key, sep, value]``. For all other cases, a ``ValueError``
             exception is raised.

info::
    "rtu" is the acronym of "Ready To Use".
        """
        if self.data == None:
            raise ValueError('no data available')

        if self.mode == VERBATIM:
            return self.data

        else:
            return [self.data[x] for x in self._KEYSEPVAL]


    def __str__(self):
        text = ['mode = "{0}"'.format(self.mode)]

        if self.data != None:
            if isinstance(self.data, str):
                text.append('data = "{0}"'.format(self.data))

            else:
                text.append("data = {0}".format(self.data))

        if self.querypath != None:
            text.append('querypath = "{0}"'.format(self.querypath))

        return "data.Infos[{0}]".format(", ".join(text))


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


====================================
The ¨peuf file used for our examples
====================================

Here is the ¨peuf file that will be used for our ¨python examples.

orpyste::
    /*
     * One example...
     */

    main::
    // Single line comment in the 1st container.

        test::
    /* Comment in a key-val block. */

            a = 1 + 9
            b <>  2

    /* Comment in the value of a key. */

            c = 3 and 4

    main::
        sub_main::
            sub_sub_main::
                verb::
                    line 1
                        line 2
                            line 3


We want blocks of this file to be defined as follows.

    1) The blocks named orpyste:``test`` are for key-value datas with either
    orpyste:``=``, or orpyste:``<>`` as a separator.

    2) The blocks named orpyste:``verb`` are for verbatim contents.

    3) All the remaining blocks are containers. This means that they are blocks
    just containing others blocks.


=========
Basic use
=========

The most important thing to do is to tell to ¨orpyste the semantic of our ¨peuf
file. This is done using the argument ``mode`` in the following ¨python script
where the variable ``content`` is the string value of our ¨peuf file (as noted
later in this section, you can work directly with a ¨peuf file).

python::
    from orpyste.data import Read

    infos = Read(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    )

    infos.build()


Let's see how we have used the argument ``mode`` (this variable is fully
presented in the documentation of ``parse.ast.AST``).

    1) ``mode`` is a dictionary having keys corresponding to kinds of blocks,
    and string values for names of blocks.
    You can use the special name ``":default:"`` so as to indicate a default
    behavior.

    2) ``"keyval:: = <>": "test"`` indicates that the blocks named
    orpyste:``test`` are for key-value datas with either orpyste:``=``, or
    orpyste:``<>`` as a separator as expected. You can indicate several names
    by using a list of strings.

    3) ``"verbatim" : "verb"`` is now easy to understand.

    4) ``"container": ":default:"`` indicates taht blocks are by default
    containers.


info::
    Instead of ``"keyval"``, you can use ``"multikeyval"`` if you want to allow
    the use of the same key several times in the same block.


info::
    All kinds of blocks have shortnames which are ``"c"``, ``"k"``, ``"mk"``
    and ``"v"`` for ``"container"``, ``"keyval"``, ``"multikeyval"`` and
    ``"verbatim"`` respectively.


It remains to see now how to access to all the datas parsed by the class
``Read`` (in the following section, we'll see how to use some queries for finding
special datas). Let's add the following lines to our previous code **(we give
later in this section an efficient and friendly way to deal with datas found)**.

...python::
    for oneinfo in infos:
        print(
            '---',
            "mode      = <<{0}>>".format(oneinfo.mode),
            "data      = <<{0}>>".format(oneinfo.data),
            "querypath = <<{0}>>".format(oneinfo.querypath),
            sep = "\n"
        )


Launching in a terminal, we see the following output.

term::
    ---
    mode      = <<keyval>>
    data      = <<None>>
    querypath = <<main/test>>
    ---
    mode      = <<keyval>>
    data      = <<{'value': '1 + 9', 'sep': '=', 'key': 'a'}>>
    querypath = <<None>>
    ---
    mode      = <<keyval>>
    data      = <<{'value': '2', 'sep': '<>', 'key': 'b'}>>
    querypath = <<None>>
    ---
    mode      = <<keyval>>
    data      = <<{'value': '3 and 4', 'sep': '=', 'key': 'c'}>>
    querypath = <<None>>
    ---
    mode      = <<verbatim>>
    data      = <<None>>
    querypath = <<main/sub_main/sub_sub_main/verb>>
    ---
    mode      = <<verbatim>>
    data      = <<line 1>>
    querypath = <<None>>
    ---
    mode      = <<verbatim>>
    data      = <<    line 2>>
    querypath = <<None>>
    ---
    mode      = <<verbatim>>
    data      = <<        line 3>>
    querypath = <<None>>


The iteration gives instances of the class ``Infos`` which have three attributs.

    1) The attribut ``'mode'`` gives the actual mode of the actual block or data.

    2) The attribut ``'data'`` is equal to ``None`` if the actual ¨info is a new
    block. Either this gives a string for one line in a verbatim content, or a
    "natural" dictionary for a key-value data.

    3) The attribut ``'querypath'`` is equal to ``None`` if the actual ¨info is
    a data. Either this gives a path like string associated to the new block
    just found.


The next ¨python snippet shows an efficient way to deal easily with blocks and datas thanks to the two methods for datas.

...python::
    for oneinfo in infos:
        if oneinfo.isnewblock:
            print('--- {0} ---'.format(oneinfo.querypath))

        else:
            print(oneinfo.rtu_data)


Launched in a terminal, we obtains the following output where for key-value
datas we obtains a list of the kind : ``[key, separator, value]``.
This is very useful because ¨python allows to use for example
``key, sep, value = ['a', '=', '1 + 9']`` such as to have directly
``key = "a"``, ``sep = "="`` and `` value = "1 + 9"``.

term::
    --- main/test ---
    ['a', '=', '1 + 9']
    ['b', '<>', '2']
    ['c', '=', '3 and 3 and 3 and 3 and 3 and 3 and 3...']
    --- main/sub_main/sub_sub_main/verb ---
    line 1
        line 2
            line 3


info::
    Here we have worked with a string, but you can work with a file using the
    class ``pathlib.Path``. The syntax remains the same.


info::
    For verbatim block contents, you can ask to keep final empty lines by adding
    orpyste::``////`` at the end of the content.


=============================
Looking for particular blocks
=============================

The iterator of the class ``Read`` can be used with a searching query on the
path like strings of the blocks. Here is an example of use where you can see
that queries use the ¨python regex syntax without leading ``^`` and the closing
``$`` (the variable ``content`` is still the string value of our ¨peuf file).

python::
    from orpyste.data import Read

    infos = Read(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    )

    infos.build()

    for query in [
        ".*",                # Anything
        "main/test",         # Only one path
        "main/sub_main/.*",  # Anything "contained" inside "main/sub_main"
    ]:
        hrule = "="*len(query)

        print("", hrule, query, hrule, sep = "\n")

        for oneinfo in datas[query]:
            if oneinfo.isnewblock:
                print(
                    "",
                    "--- {0} [{1}] ---".format(oneinfo.querypath, oneinfo.mode),
                    sep = "\n"
                )

            else:
                print(oneinfo.rtu_data)


This gives the following ouputs as expected.

term::
    ==
    .*
    ==

    --- main/test [keyval] ---
    ['aaa', '=', '1 + 9']
    ['bbbbbbbbb', '<>', '2']
    ['c', '=', '3 and 3 and 3 and 3 and 3 and 3 and 3...']

    --- main/sub_main/sub_sub_main/verb [verbatim] ---
    line 1
        line 2
            line 3

    =========
    main/test
    =========

    --- main/test [keyval] ---
    ['aaa', '=', '1 + 9']
    ['bbbbbbbbb', '<>', '2']
    ['c', '=', '3 and 3 and 3 and 3 and 3 and 3 and 3...']

    ================
    main/sub_main/.*
    ================

    --- main/sub_main/sub_sub_main/verb [verbatim] ---
    line 1
        line 2
            line 3
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
            self.walk_view.write(
                Infos(
                    querypath = "/".join(self._qpath),
                    mode      = self.last_mode
                )
            )

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
This iterator is very basic: it yields the instances of ``Infos`` found during
the analyze of the ¨peuf file.
        """
        for infos in self.walk_view:
            yield infos


    def __getitem__(self, querypath):
        """
prototype::
    arg = str: querypath ;
          this a query using the ¨python regex syntax without the leading ``^``
          and the closing ``$``


We hack the get item ¨python syntax via hooks so as to have an iterator
accepting queries (see the last section of the documentation of the class
for an example).
        """
# What has to be extracted ?
        query_pattern = re.compile("^{0}$".format(querypath))

# We can now extract the matching infos.
        datasfound = False
        newblock   = True

        for infos in self.walk_view:
            if infos.isnewblock:
                datasfound = query_pattern.search(infos.querypath)

                if datasfound:
                    yield infos

            elif datasfound:
                yield infos
