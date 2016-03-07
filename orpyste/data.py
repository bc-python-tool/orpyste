#! /usr/bin/env python3

"""
prototype::
    date = 2016-03-07


This module is for reading and extractings easily ¨infos in ¨peuf files.
"""

from collections import OrderedDict
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
        if meth.__name__ == "add_keyval":
            nbline = self.kv_nbline

        else:
            nbline = self.nbline

        self.walk_view.write(
            Infos(
                data   = args[0],
                mode   = self.last_mode,
                nbline = nbline
            )
        )

        return meth(self, *args, **kwargs)

    return newmeth


# ----------- #
# -- INFOS -- #
# ----------- #

START_TAG = ":start:"
END_TAG   = ":end:"

class Infos():
    """
prototype::
    see = Read, ReadBlock

    arg-attr = None , str: querypath = None ;
               a file like path used to walk in datas using ¨python regexes
               without opening ``^`` and closing ``$``
    arg-attr = None , str: mode = None ;
               the mode of a block or a data
    arg-attr = None , str , {'sep': str, 'key': str, 'value': str}: data = None ;
               the datas found if the mode is for one data
    arg-attr = int: nbline = -1 ;
               the number of the line of the infos

    arg-attr = bool: islinebyline = True;
               datas can be returned line by line or block by block


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
        querypath    = None,
        mode         = None,
        data         = None,
        nbline       = -1,
        islinebyline = True
    ):
        self.querypath    = querypath
        self.mode         = mode
        self.data         = data
        self.nbline       = nbline
        self.islinebyline = islinebyline


    def isblock(self):
        return self.querypath not in [None, START_TAG, END_TAG]

    def isdata(self):
        return self.data != None

    def isstart(self):
        return self.querypath == START_TAG

    def isend(self):
        return self.querypath == END_TAG


    @property
    def rtu_data(self):
        """
prototype::
    return = if self.islinebyline == True then str ,
                                               [str, str, str]
             else [(int, str),...] ,
                  OrderedDict((int, str): {"key": str, "val": val});
             if we have no data, a ``ValueError`` exception is raised,
             otherwise friendly version of datas is returned


If ``self.islinebyline`` is ``True``, the datas looks as it follows.

    1) For a verbatim content the actual line is returned.

    2) For a key-value content that is a list looking like ``[key, sep, value]``.


If ``self.islinebyline`` is ``False``, the datas are of the following kinds
where ``nbline`` refers to the number line in the ¨peuf file (this can be useful
for raising errors to the user or for the ``"multikeyval"`` mode).

    1) For a verbatim content, a list of ``(nbline, verbatim_line)`` like tuples
    is returned.

    2) For a key-value content, the method returns an ordered dictionary with
    ``(nbline, key)`` like tuples for keys, and ``{"sep": ..., "val": ...}``
    like dictionary for values.


info::
    If ``self.islinebyline`` is ``True``, the user can access the number line
    in the ¨peuf file simply by using ``self.nbline``


info::
    "rtu" is the acronym of "Ready To Use".
        """
        if self.data == None:
            raise ValueError('no data available')

# Line by line delivery
        if self.islinebyline:
            if self.mode == VERBATIM:
                return self.data

            else:
                return tuple(self.data[x] for x in self._KEYSEPVAL)

# Block by block delivery
        else:
            return self.data

    @property
    def short_rtu_data(self):
        """
prototype::
    see = self.rtu_data


If ``self.islinebyline == False``, an ``ValueError`` error is raised, otherwise
this method gives the same kind of values than ``self.rtu_data`` but without any
number line.


warning::
    For the ``"multikeyval"`` mode, if the keys is met two times, an error will
    be raised (the number line is also used to diiferentiate the same key used
    at different places in a ``"multikeyval"`` block).
        """
        if self.data == None:
            raise ValueError('no data available')

        if self.islinebyline:
            raise ValueError('no short data for a line by line delivery')

        if self.mode == "verbatim":
            return [line for (nb, line) in self.data]

        else:
            data = OrderedDict()

            for (nb, key), val in self.data.items():
                if key in data:
                    raise ValueError(
                        "output impossible because the key "
                        + "<< {0} >> ".format(key) +
                        "has been already used"
                    )

                data[key] = val

            return data

    def __str__(self):
        text = ['mode = {0}'.format(repr(self.mode))]

        if self.data != None:
            if isinstance(self.data, str):
                text.append('data = "{0}"'.format(self.data))

            else:
                text.append("data = {0}".format(self.data))

        if self.querypath != None:
            text.append('querypath = "{0}"'.format(self.querypath))

        return "data.Infos[{0}]".format(", ".join(text))


# -------------------------- #
# -- READING LINE BY LINE -- #
# -------------------------- #

OPEN, CLOSE = "open", "close"
DATAS_MODES = [KEYVAL, MULTIKEYVAL, VERBATIM]

START_BLOCK = Infos(START_TAG)
END_BLOCK   = Infos(END_TAG)


class Read(WalkInAST):
    """
prototype::
    see = parse.ast.AST , parse.walk.WalkInAST

    arg-attr = pathlib.Path, str: content ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str, dict: mode ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str: encoding = "utf-8" ;
               see the documentation of ``parse.ast.AST``


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
            "nbline    = <<{0}>>".format(oneinfo.nbline),
            sep = "\n"
        )


Launching in a terminal, we see the following output where you can note that
special blocks indicate the begin and the end of the iteration.

term::
    ---
    mode      = <<None>>
    data      = <<None>>
    querypath = <<:start:>>
    nbline    = <<-1>>
    ---
    mode      = <<keyval>>
    data      = <<None>>
    querypath = <<main/test>>
    nbline    = <<8>>
    ---
    mode      = <<keyval>>
    data      = <<{'sep': '=', 'key': 'a', 'value': '1 + 9'}>>
    querypath = <<None>>
    nbline    = <<11>>
    ---
    mode      = <<keyval>>
    data      = <<{'sep': '<>', 'key': 'b', 'value': '2'}>>
    querypath = <<None>>
    nbline    = <<12>>
    ---
    mode      = <<keyval>>
    data      = <<{'sep': '=', 'key': 'c', 'value': '3 and 4'}>>
    querypath = <<None>>
    nbline    = <<16>>
    ---
    mode      = <<verbatim>>
    data      = <<None>>
    querypath = <<main/sub_main/sub_sub_main/verb>>
    nbline    = <<21>>
    ---
    [...]
    ---
    mode      = <<None>>
    data      = <<None>>
    querypath = <<:end:>>
    nbline    = <<-1>>
    ---


The iteration gives instances of the class ``Infos`` which have three attributs.

    1) The attribut ``'mode'`` gives the actual mode of the actual block or data
    (the special blocks for start and end have no mode).

    2) The attribut ``'data'`` is equal to ``None`` if the actual ¨info is a new
    block. Either this gives a string for one line in a verbatim content, or a
    "natural" dictionary for a key-value data.

    3) The attribut ``'querypath'`` is equal to ``None`` if the actual ¨info is
    a data, or one of the special blocks for start and end.
    Otherwise the attribut ``'querypath'`` gives a path like string associated
    to the new block just found.


The next ¨python snippet shows an efficient way to deal easily with blocks and
datas thanks to the methods ``isblock`` and ``isdata``
((
    There are also methods ``isstart`` and ``isend``. The later can be really
    usefull.
)),
together with the property method ``rtu_data`` of the class ``data.Infos``.

...python::
    for oneinfo in infos:
        if oneinfo.isblock():
            print('--- {0} ---'.format(oneinfo.querypath))

        elif oneinfo.isdata():
            print(oneinfo.rtu_data)


Launched in a terminal, we obtains the following output where for key-value
datas we obtains a list of the kind : ``(key, separator, value)``. This is
very useful because ¨python allows to use for example
``key, sep, value = ('a', '=', '1 + 9')`` such as to have directly
``key = "a"``, ``sep = "="`` and `` value = "1 + 9"``.

term::
    --- main/test ---
    ('a', '=', '1 + 9')
    ('b', '<>', '2')
    ('c', '=', '3 and 4')
    --- main/sub_main/sub_sub_main/verb ---
    line 1
        line 2
            line 3


info::
    For verbatim block contents, you can ask to keep final empty lines by adding
    orpyste::``////`` at the end of the content.


info::
    Here we have worked with a string, but you can work with a file using the
    class ``pathlib.Path``. The syntax remains the same.


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
        title = "Query: {0}".format(query)
        hrule = "="*len(title)

        print("", hrule, title, hrule, sep = "\n")

        for oneinfo in datas[query]:
            if oneinfo.isblock():
                print(
                    "",
                    "--- {0} [{1}] ---".format(
                        oneinfo.querypath,
                        oneinfo.mode
                    ),
                    sep = "\n"
                )

            else:
                print(oneinfo.rtu_data)


This gives the following ouputs as expected.

term::
    =========
    Query: .*
    =========

    --- main/test [keyval] ---
    ('aaa', '=', '1 + 9')
    ('bbbbbbbbb', '<>', '2')
    ('c', '=', '3 and 4')

    --- main/sub_main/sub_sub_main/verb [verbatim] ---
    line 1
        line 2
            line 3

    ================
    Query: main/test
    ================

    --- main/test [keyval] ---
    ['aaa', '=', '1 + 9']
    ['bbbbbbbbb', '<>', '2']
    ('c', '=', '3 and 4')

    =======================
    Query: main/sub_main/.*
    =======================

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
                    mode      = self.last_mode,
                    nbline    = self.nbline
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
prorotype::
    see = self.__getitem__


This iterator is very basic.

    1) First a special instance of ``Infos`` indicating the starting of the
    iteration is yielded.

    2) Then the instances of ``Infos`` found during the analyze of the ¨peuf
    file are yielded.

    3) A special instance of ``Infos`` is finally yielded so as to indicate
    that the iteration is finished.
        """
        yield START_BLOCK
        yield from self[".*"]
        yield END_BLOCK


    def __getitem__(self, querypath):
        """
prototype::
    arg = str: querypath ;
          this a query using the ¨python regex syntax without the leading
          ``^`` and the closing ``$``


We hack the get item ¨python syntax via hooks so as to have an iterator
accepting queries (see the last section of the documentation of the class
for an example of use of queries).
        """
# What has to be extracted ?
        query_pattern = re.compile("^{0}$".format(querypath))

# We can now extract the matching infos.
        datasfound = False

        for oneinfo in self.walk_view:
            if oneinfo.isblock():
                datasfound = query_pattern.search(oneinfo.querypath)

                if datasfound:
                    yield oneinfo

            elif datasfound:
                yield oneinfo


# ---------------------------- #
# -- READING BLOCK BY BLOCK -- #
# ---------------------------- #

class ReadBlock(Read):
    """
prototype::
    see = Read


=====================================================
``ReadBlock`` is near to ``Read`` but still different
=====================================================

The only real difference between the classes ``ReadBlock`` and ``Read`` is that
the former returns the datas block by block, whereas the second one gives line
by line informations (with huge files, the line by line readers is a better one).


warning::
    Take a look first at the documentation of the class ``Read`` because we are
    going to give only new informations regarding to this class.


====================================
The ¨peuf file used for our examples
====================================

Here is the uncommented ¨peuf file that will be used for our ¨python examples where the block orpyste:``test`` has key-value datas, and orpyste:``verb`` uses
a verbatim content.

orpyste::
    main::
        test::
            a = 1 + 9
            b <>  2
            c = 3 and 4

    main::
        sub_main::
            sub_sub_main::
                verb::
                    line 1
                        line 2
                            line 3


=====================
Reading, the hard way
=====================

Let's see how the datas are roughly sent by the basic iterator of the class
``ReadBlock``.

python::
    from orpyste.data import ReadBlock

    infos = ReadBlock(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    )

    infos.build()

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
    mode      = <<None>>
    data      = <<None>>
    querypath = <<:start:>>
    ---
    mode      = <<keyval>>
    data      = <<None>>
    querypath = <<main/test>>
    ---
    mode      = <<keyval>>
    data      = <<OrderedDict([((11, 'aaa'), {'val': '1 + 9', 'sep': '='}), ((12, 'bbbbbbbbb'), {'val': '2', 'sep': '<>'}), ((16, 'c'), {'val': '3 and 3 and 3 and 3 and 3 and 3 and 3...', 'sep': '='})])>>
    querypath = <<None>>
    ---
    mode      = <<verbatim>>
    data      = <<None>>
    querypath = <<main/sub_main/sub_sub_main/verb>>
    ---
    mode      = <<verbatim>>
    data      = <<[(22, 'line 1'), (23, '    line 2'), (24, '        line 3')]>>
    querypath = <<None>>
    ---
    mode      = <<None>>
    data      = <<None>>
    querypath = <<:end:>>


The iteration still gives instances of the class ``Infos`` but with different
kinds of datas reagrding to the ones obtained with the class ``Read``.






    1) For a verbatim content, a list of ``(nbline, verbatim_line)`` like tuples
    is returned.

    2) For a key-value content, the method returns an ordered dictionary with
    ``(nbline, key)`` like tuples for keys, and ``{"sep": ..., "val": ...}``
    like dictionary for values.


We can still asks to have easier to use datas thanks to the property method
``rtu_data`` of the class ``data.Infos``.

...python::
    for oneinfo in infos:
        if oneinfo.isblock():
            print('--- {0} ---'.format(oneinfo.querypath))

        elif oneinfo.isdata():
            pprint(oneinfo.rtu_data)


Launched in a terminal, we obtains the following output (where the dictionary is
indeed an ordered one).

term::
    --- main/test ---
    {(11, 'aaa'): {'sep': '=', 'val': '1 + 9'},
     (12, 'bbbbbbbbb'): {'sep': '<>', 'val': '2'},
     (16, 'c'): {'sep': '=', 'val': '3 and 3 and 3 and 3 and 3 and 3 and 3...'}}
    --- main/sub_main/sub_sub_main/verb ---
    [(22, 'line 1'), (23, '    line 2'), (24, '        line 3')]


If you really do not want to have the number of lines, you can use the additional property method ``short_rtu_data`` like ine the following code.

...python::
    for oneinfo in infos:
        if oneinfo.isblock():
            print('--- {0} ---'.format(oneinfo.querypath))

        elif oneinfo.isdata():
            pprint(oneinfo.short_rtu_data)

In a terminal we have the following printings.

term::



=============================
Looking for particular blocks
=============================

See the documentation of the class ``Read``. Regarding to the class ``Read``,
just the ouputs of the class ``ReadBlock`` are different but the way to use
queries remains the same.
    """

    def _addblockdata(self, oneinfo):
        if self._lastmode == "verbatim":
            self._datas.append((oneinfo.nbline, oneinfo.data))

        else:
            key, sep, val = oneinfo.rtu_data

            self._datas[(oneinfo.nbline, key)] = {
                "sep" : sep,
                "val" : val
            }


    def __getitem__(self, querypath):
        """
prototype::
    see = Read.__getitem__
        """
# What has to be extracted ?
        query_pattern = re.compile("^{0}$".format(querypath))

# We can now extract the matching infos.
        datasfound  = False
        self._datas = None

        for oneinfo in self.walk_view:
            if oneinfo.isblock():
                datasfound = query_pattern.search(oneinfo.querypath)

                if datasfound:
                    if self._datas != None:
                        yield Infos(
                            mode         = self._lastmode,
                            data         = self._datas,
                            islinebyline = False
                        )

                    self._lastmode = oneinfo.mode

                    if self._lastmode == "verbatim":
                        self._datas = []

                    else:
                        self._datas = OrderedDict()

                    yield oneinfo


            elif datasfound:
                self._addblockdata(oneinfo)


        if self._datas != None:
            yield Infos(
                mode         = oneinfo.mode,
                data         = self._datas,
                islinebyline = False
            )

        self._datas    = None
        self._lastmode = None
