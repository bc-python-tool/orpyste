#! /usr/bin/env python3

"""
prototype::
    date = 2017-07-30


This module is for reading and extractings easily ¨infos in ¨peuf files.
"""

from collections import OrderedDict
from copy import deepcopy
from json import dumps, load, loads
import re

from orpyste.parse.walk import *


# ----------------------------------- #
# -- DECORATOR(S) FOR THE LAZY MAN -- #
# ----------------------------------- #

def adddata(meth):
    """
prototype::
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

        data = args[0]

        self.walk_view.write(
            Infos(
                data   = data,
                mode   = self.last_mode,
                nbline = nbline
            )
        )

        return meth(self, *args, **kwargs)

    return newmeth


# -------------- #
# -- REGPATHS -- #
# -------------- #

# All the codes for regpaths come directly from the module ``mistool.os_use``
# where they are maintained.

# There is just a "little big" difference with the original code : the
# following version always returns a compiled regex, instead of a string to be
# compiled.

REGPATH_SPE_CHARS = ['*', '**', '.', '@', '×']

REGPATH_TO_REGEX = {
    '**': '.+',
    '.': '\\.',
    '/': '[^/]+',
    '@': '.',
    '\\': '[^\\]+',
    '×': '*'
}

RE_SPECIAL_CHARS = re.compile('(?<!\\\\)((?:\\\\\\\\)*)((\\*+)|(@)|(×)|(\\.))')


def regexify(pattern, sep = "/"):
    """
prototype::
    arg = str: pattern ;
          ``pattern`` is a regpath pattern using a syntax which tries to catch
          the best of the regex and the Unix-glob syntaxes
    arg = str: sep = "/" ;
          this indicates an ¨os like separator

    return = _sre.SRE_Pattern ;
             a compiled regex version of ``pattern``.


====================
Some examples of use
====================

The next section gives all the difference between the regpath patterns and the
regexes of ¨python.


Let suppose fisrt that we want to find paths without any ``/`` the default
value of the argument ``sep`` that finish with either path::``.py`` or
path::``.txt``. The code below shows how ``regexify`` gives easily an
uncompiled regex pattern to do such searches.

pyterm::
    >>> from orpyste.data import regexify
    >>> print(regexify("*.(py|txt)"))
    re.compile('[^/]+\.(py|txt)')


Let suppose now that we want to find paths that finish with either
path::``.py`` or path::``.txt``, and that can also be virtually or really
found recursivly when walking in a directory. Here is how to use ``regexify``.

pyterm::
    >>> from orpyste.data import regexify
    >>> print(regexify("**.(py|txt)"))
    re.compile('.+\.(py|txt)')


=============================
A Unix-glob like regex syntax
=============================

Here are the only differences between the Unix-glob like regex syntax with the
Unix-glob syntax and the traditional regexes.

    1) ``*`` indicates one ore more characters except the separator of the OS.
    This corresponds to the regex regex::``[^\\]+`` or regex::``[^/]+``
    regarding to the OS is Windows or Unix.

    2) ``**`` indicates one ore more characters even the separator of the OS.
    This corresponds to the regex regex::``.+``.

    3) ``.`` is not a special character, this is just a point. This corresponds
    to regex::``\.`` in regexes.

    4) The multiplication symbol ``×`` is the equivalent of regex::``*`` in
    regexes. This allows to indicate zero or more repetitions.

    5) ``@`` is the equivalent of regex::``.`` in regexes. This allows to
    indicate any single character except a newline.

    6) ``\`` is an escaping for special character. For example, you have to use
    a double backslash ``\\`` to indicate the Windows separator ``\``.
    """
    onestar2regex = REGPATH_TO_REGEX[sep]

    newpattern = ""
    lastpos    = 0

    for m in RE_SPECIAL_CHARS.finditer(pattern):
        spechar = m.group()

        if spechar not in REGPATH_SPE_CHARS:
            raise ValueError("too much consecutive stars ''*''")

        spechar     = REGPATH_TO_REGEX.get(spechar, onestar2regex)
        newpattern += pattern[lastpos:m.start()] + spechar
        lastpos     = m.end()

    newpattern += pattern[lastpos:]
    newpattern  = re.compile("^{0}$".format(newpattern))

    return newpattern


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
    arg-attr = data = None ;
               the datas found if the mode is for some datas
    arg-attr = int: nbline = -1 ;
               the number of the line of the datas


Here are some examples.

    * ``mode = "keyval"`` and ``querypath = "main/test"``.
    * ``mode = "keyval"`` and ``data = {'sep = '=', 'key = 'a', 'value = '1'}``.
    * ``mode = VERBATIM`` and ''querypath = "main/sub_main/verb"''.
    * ``mode = "verbatim"`` and ``data = "One line..."``.
    * ``mode = "verbatim"`` and ``data = ("Line #1", "Line #2", ...)``.
    * ... ¨etc.
    """

    def __init__(
        self,
        querypath  = None,
        mode       = None,
        data       = None,
        nbline     = -1
    ):
        self.querypath = querypath
        self.mode      = mode
        self.nbline    = nbline

        if isinstance(data, list):
            data = tuple(data)

        self.data = data

    def isblock(self):
        return self.querypath not in [None, START_TAG, END_TAG]

    def isdata(self):
        return self.data is not None

    def isstart(self):
        return self.querypath == START_TAG

    def isend(self):
        return self.querypath == END_TAG

    def yrtu(self):
        """
prototype::
    see = self.rtu

    yield = tuple(int, str, str, str)
          | tuple(int, str) ;
            the values yield looks like either ``(nbline, verbatim_line)`` for
            a verbatim line, or ``(nbline, key, sep, value)`` for a key-value
            content

This method only yield "single" datas even for the block contents build by the
class ``ReadBlock``.

info::
    "yrtu" is the acronym of "Yield Ready To Use".
        """
        rtu = self.rtu

# [BLOCK MODE] Key-value
        if isinstance(rtu, MKOrderedDict):
            for (_, key), dicval in rtu.items():
                yield (
                    dicval["nbline"],
                    key,
                    dicval["sep"],
                    dicval["value"]
                )

# [INLINE MODE - Unusefull but none blocking behavior]
        elif isinstance(rtu[0], int):
            yield rtu

# [BLOCK MODE] Verbatim
        else:
            for dicval in rtu:
                yield (dicval["nbline"], dicval["value"])

    @property
    def rtu(self):
        """
prototype::
    return = ? ;
             if we have no data, a ``ValueError`` exception is raised,
             otherwise a "friendly" version of the datas is returned


The datas have one of the following formats.

    1) For a single verbatim content, a tuple ``(nbline, verbatim_line)`` is
    returned.

    2) For a single key-value content, a tuple ``(nbline, key, sep, value)``
    is returned.

    3) For block contents, either a tuple of dictionaries ``{'nbline': ...,
    'value': ...}`` or an instance of ``MKOrderedDict`` is returned.


info::
    "rtu" is the acronym of "Ready To Use".
        """
        if self.data is None:
            raise ValueError('no data available')

# [SINGLE] Verbatim line
        elif isinstance(self.data, str):
            return (self.nbline, self.data)

# [SINGLE] Key-value
        elif isinstance(self.data, dict):
            return tuple(
                [self.nbline] + [self.data[x] for x in KEYVAL_TAGS]
            )

# [SEVERAL] Key-value
# [SEVERAL] Verbatim lines
        else:
            return self.data

    def __str__(self):
        text = ['mode = {0}'.format(repr(self.mode))]

        if self.data is not None:
            if isinstance(self.data, str):
                text.append('data = "{0}"'.format(self.data))

            else:
                text.append("data = {0}".format(self.data))

        if self.querypath is not None:
            text.append('querypath = "{0}"'.format(self.querypath))

        return "data.Infos[{0}]".format(", ".join(text))


# -------------------------- #
# -- READING LINE BY LINE -- #
# -------------------------- #

FLAT_TAG, TREE_TAG = "flat", "tree"

START_BLOCK = Infos(START_TAG)
END_BLOCK   = Infos(END_TAG)

class Read(WalkInAST):
    """
prototype::
    see = parse.ast.AST , parse.walk.WalkInAST , regexify


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


We want the blocks of this file to be defined as follows.

    1) The blocks named orpyste::``test`` are for single key-value datas with
    either orpyste::``=``, or orpyste::``<>`` as a separator.

    2) The blocks named orpyste::``verb`` are for verbatim contents.

    3) All the remaining blocks are containers. This means that they are blocks
    just containing others blocks.


=========
Basic use
=========

info::
    We will work with a string for the ¨peuf content to be analyzed, but you
    can work with a file using the class ``pathlib.Path`` directly instead of
    the string. The syntax remains the same.


The most important thing to do is to tell to ¨orpyste the semantic of our ¨peuf
file. This is done using the argument ``mode`` in the following partial ¨python
script where the variable ``content`` is the string value of our ¨peuf file. As
you can see we can use a context ``with Read(...) as ...: ...``.

python::
    from orpyste.data import Read

    with Read(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    ) as datas:
        ...


Let's see how we have used the argument ``mode`` (this variable is fully
presented in the documentation of ``parse.ast.AST``).

    1) ``mode`` is a dictionary having keys corresponding to kinds of blocks,
    and string values for names of blocks.
    You can use the special name ``":default:"`` so as to indicate a default
    behavior.

    2) ``"keyval:: = <>": "test"`` indicates that the blocks named
    orpyste::``test`` are for key-value datas with either orpyste::``=``, or
    orpyste::``<>`` as a separator as expected. You can indicate several names
    by using a list of strings.

    3) ``"verbatim" : "verb"`` is now easy to understand.

    4) ``"container": ":default:"`` indicates taht blocks are by default
    containers.

    5) When you call the context manager, indeed the class uses, more or less,
    the methods ``build`` when the context is opened, and ``remove_extras`` to
    close the context (see the class ``parse.walk.WalkInAST``).


info::
    Instead of ``"keyval"``, you can use ``"multikeyval"`` if you want to allow
    the use of the same key several times in the same block.


info::
    All kinds of blocks have shortnames which are ``"c"``, ``"k"``, ``"mk"``
    and ``"v"`` for ``"container"``, ``"keyval"``, ``"multikeyval"`` and
    ``"verbatim"`` respectively.


It remains to see now how to access to all the datas parsed by the class
``Read`` (in the following section, we'll see how to use some queries for
finding special datas). Let's add the following lines to our previous code
**(we give later in this section an efficient and friendly way to deal with
datas found)**.

...python::
    with Read(...) as datas:
        for onedata in datas:
            print(
                '---',
                "mode      = <<{0}>>".format(onedata.mode),
                "data      = <<{0}>>".format(onedata.data),
                "querypath = <<{0}>>".format(onedata.querypath),
                "nbline    = <<{0}>>".format(onedata.nbline),
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
    data      = <<{'sep': '=', 'value': '1 + 9', 'key': 'a'}>>
    querypath = <<None>>
    nbline    = <<11>>
    ---
    [...]
    ---
    mode      = <<verbatim>>
    data      = <<None>>
    querypath = <<main/sub_main/sub_sub_main/verb>>
    nbline    = <<21>>
    ---
    mode      = <<verbatim>>
    data      = <<line 1>>
    querypath = <<None>>
    nbline    = <<22>>
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
together with the property method ``rtu`` of the class ``data.Infos``.

...python::
    with Read(...) as datas:
        for onedata in datas:
            if onedata.isblock():
                print('--- {0} ---'.format(onedata.querypath))

            elif onedata.isdata():
                print(onedata.rtu)


Launched in a terminal, we obtains the following output where for key-value
datas we obtains lists of the kinds  ``(nbline, line)`` for verbatim lines,
and  ``(nbline, key, separator, value)`` for keys and their value.

term::
    --- main/test ---
    (11, 'a', '=', '1 + 9')
    (12, 'b', '<>', '2')
    (16, 'c', '=', '3 and 4')
    --- main/sub_main/sub_sub_main/verb ---
    (22, 'line 1')
    (23, '    line 2')
    (24, '        line 3')


info::
    For verbatim block contents, you can ask to keep final empty lines by adding
    orpyste::``////`` at the end of the content.


info::
    Remember that ¨python allows to use
    ``nbline, key, sep, value = (11, 'a', '=', '1 + 9')``
    such as to have directly
    ``nbline = 11``, ``key = "a"``, ``sep = "="`` and `` value = "1 + 9"``.

    You can even use ``_, key, _, value = (11, 'a', '=', '1 + 9')`` such as to
    only keep keys and their values.


=============================
Looking for particular blocks
=============================

The iterator of the class ``Read`` can be used with a searching query on the
"querypaths". Here is an example of use where you can see that queries use the
merly ¨python like regex syntax without the leading ``^`` and the closing
``$`` (the variable ``content`` is still the string value of our ¨peuf file).
Take a look at the documentation of the function ``regexify`` to see how to use
your own regex like queries.

python::
    from orpyste.data import Read

    with Read(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    ) as datas:
        for query in [
            "main/test",    # Only one path
            "**",           # Anything
            "main/*",       # Anything "contained" inside "main/test"
        ]:
            title = "Query: {0}".format(query)
            hrule = "="*len(title)

            print("", hrule, title, hrule, sep = "\n")

            for onedata in datas[query]:
                if onedata.isblock():
                    print(
                        "",
                        "--- {0} [{1}] ---".format(
                            onedata.querypath,
                            onedata.mode
                        ),
                        sep = "\n"
                    )

                else:
                    print(onedata.rtu)


This gives the following outputs as expected.

term::
    ================
    Query: main/test
    ================

    --- main/test [keyval] ---
    (11, 'a', '=', '1 + 9')
    (12, 'b', '<>', '2')
    (16, 'c', '=', '3 and 4')

    =========
    Query: **
    =========

    --- main/test [keyval] ---
    (11, 'a', '=', '1 + 9')
    (12, 'b', '<>', '2')
    (16, 'c', '=', '3 and 4')

    --- main/sub_main/sub_sub_main/verb [verbatim] ---
    (22, 'line 1')
    (23, '    line 2')
    (24, '        line 3')

    =============
    Query: main/*
    =============

    --- main/test [keyval] ---
    (11, 'a', '=', '1 + 9')
    (12, 'b', '<>', '2')
    (16, 'c', '=', '3 and 4')
    """

# -- START AND END OF THE WALK -- #
    def start(self):
        self._verblines = []
        self._keyval    = []
        self._qpath     = []

# -- NO SECTION ALLOWED HERE ! -- #
    def open_section(self):
        raise ValueError(
            "section forbiden with this class : use the module ``section``"
        )

# -- FOR BLOCKS -- #
    def open_block(self, name):
        self._qpath.append(name)

        if self.last_mode in [KEYVAL, MULTIKEYVAL, VERBATIM]:
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

# -- DATAS: (MULTI)KEYVAL & VERBATIM -- #
    @adddata
    def add_keyval(self, keyval):
        ...

    @adddata
    def add_line(self, line):
        ...

# -- USER FRIENDLY ITERATORS -- #
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
        yield from self["**"]
        yield END_BLOCK

    def __getitem__(self, querypath):
        """
prototype::
    arg = str: querypath ;
          this a query using the ¨python regex syntax without the leading
          ``^`` and the closing ``$``


We hack the get item ¨python syntax via hooks so as to have an iterator
accepting queries (see the last section of the main documentation of this
class for an example of use).
        """
# What has to be extracted ?
        query_pattern = regexify(querypath)

# We can now extract the matching infos.
        infosfound = False

        for oneinfo in self.walk_view:
            if oneinfo.isblock():
                infosfound = query_pattern.search(oneinfo.querypath)

                if infosfound:
                    yield oneinfo

            elif infosfound:
                yield oneinfo


# ---------------------------- #
# -- READING BLOCK BY BLOCK -- #
# ---------------------------- #

STD_TAG          = "std"
MYDICT_KIND_TAGS = set([FLAT_TAG, TREE_TAG])

NOSEP_TAG, NONB_TAG, NOVAL_TAG = "nosep", "nonb", "noval"
NOTHING_TAGS                   = set([NOSEP_TAG, NONB_TAG, NOVAL_TAG])

_NO_DICT_KEY = {
    NOSEP_TAG: SEP_TAG,
    NONB_TAG : NBLINE_TAG,
    NOVAL_TAG: VAL_TAG
}

MYDICT_TAGS = MYDICT_KIND_TAGS | NOTHING_TAGS
MYDICT_TAGS.add(STD_TAG)

MINI_TAG = "mini"

MYDICT_ALIAS_TAGS = {
    MINI_TAG: set([NOSEP_TAG, NONB_TAG])
}


class ReadBlock(Read):
    """
=============================================================
``ReadBlock`` is similar to ``Read`` but not exactly the same
=============================================================

The main difference between the classes ``ReadBlock`` and ``Read`` is that the
former returns the datas block by block, whereas the second one gives the datas
line by line (with huge files, a line by line reader is a better tool).


info::
    Take first a look at the documentation of the class ``Read`` because we are
    going to give only new informations regarding to the class ``ReadBlock``.


====================================
The ¨peuf file used for our examples
====================================

Here is the uncommented ¨peuf file that will be used for our ¨python examples
where the block orpyste::``test`` has key-value datas, and orpyste::``verb``
uses a verbatim content.

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


==================================
Working with a friendly dictionary
==================================

The property ``flatdict`` gives an ordered dictionnary with keys equal to
``(id, querypaths)`` where ``id`` is an id number allowing the use of the same
"paths" for blocks in different places of a ¨peuf content.
Let's consider the following code where ``content`` is the string given in the
first section.

python::
    from pprint import pprint

    from orpyste.data import ReadBlock

    with ReadBlock(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    ) as datas:
        pprint(datas.flatdict)


Here is what is obtained when the code is launching in a terminal (the ouput
has been hand formatted). You can see that verbatim contents are stored line
by line and not in a single string !

term::
    MKOrderedDict([
        (
            id=0, key='main/test',
            value=MKOrderedDict([
                (id=0, key='a',
                 value={'value': '1 + 9', 'sep': '=', 'nbline': 3}),
                (id=0, key='b',
                 value={'value': '2', 'sep': '<>', 'nbline': 4}),
                (id=0, key='c',
                 value={'value': '3 and 4', 'sep': '=', 'nbline': 5})
                ])
        ),
        (
            id=0, key='main/sub_main/sub_sub_main/verb',
            value=({'value': 'line 1', 'nbline': 11},
                   {'value': 'line 2', 'nbline': 12},
                   {'value': 'line 3', 'nbline': 13})
        )
    ])

As you can see you will have to work with a ``MKOrderedDict`` which is indeed
implemented in the module ``parse.walk``. This is necessary regarding to the
mode ``"multikeyval"``. You can merly work with ``MKOrderedDict`` as you will
do with dictionaries as you can see in the following example.

python::
    with ReadBlock(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    ) as datas:
        print("--- With ID numbers ---")

        for (idkey, key), value in datas.flatdict.items():
            print((idkey, key))

        print("--- Without ID numbers ---")

        for key, value in datas.flatdict.items(noid = True):
            print(key)


term::
    --- With ID numbers ---
    (0, 'main/test')
    (0, 'main/sub_main/sub_sub_main/verb')
    --- Without ID numbers ---
    main/test
    main/sub_main/sub_sub_main/verb


===============================
Working with other dictionaries
===============================

warning::
    In this section we consider the same ¨peuf content as in the preceding one.
    So we don't give all details in the ¨python snippets.


Sometimes it is easier to work with a dictionary reflecting the tree structure
of the blocks in the ¨peuf file. For that feature, you can use the property
named ``treedict`` like in the following incomplete code.

...python::
    with ReadBlock(...) as datas:
        pprint(datas.treedict)


Here is what is obtained when the code is launching in a terminal (the ouput
has been hand formatted).

term::
    RecuOrderedDict([
        ('main', RecuOrderedDict([
            ('test', RecuOrderedDict([
                ('a', {'value': '1 + 9', 'sep': '=', 'nbline': 3}),
                ('b', {'value': '2', 'sep': '<>', 'nbline': 4}),
                ('c', {'value': '3 and 4', 'sep': '=', 'nbline': 5})
            ])),
            ('sub_main', RecuOrderedDict([
                ('sub_sub_main', RecuOrderedDict([
                    ('verb', ({'value': 'line 1', 'nbline': 11},
                              {'value': 'line 2', 'nbline': 12},
                              {'value': 'line 3', 'nbline': 13}))
                ]))
            ]))
        ]))
    ])


As you can see you will have to work with a ``RecuOrderedDict`` which is indeed
implemented in the module ``parse.walk``.
This kind of dictionary has useful functionnalities : for example, you can use
``datas.treedict[['test', 'sub_main', 'sub_sub_main']]`` instead of
``datas.treedict['test']['sub_main']['sub_sub_main']``.


You can have a little more customizable dictionary thanks to the methdo
``mydict``. Here is an example of use where we don't want to keep the
separators and the numbers of the lines.

...python::
    with ReadBlock(...) as datas:
        print(datas.mydict("std nosep nonb"))


This will produce in a terminal the followin lines (the ouput has been hand
formatted).

term::
    {
        'main/test': {'b': '2', 'c': '3 and 4', 'a': '1 + 9'},
        'main/sub_main/sub_sub_main/verb': ('line 1', 'line 2', 'line 3')
    }


Here is another similar example of use but we a tree like dictionary.

...python::
    with ReadBlock(...) as datas:
        pprint(datas.mydict("tree nosep nonb"))


In that case, we obtain the following output in a terminal (some formattings
have been done by hand).

term::
    RecuOrderedDict([
        ('main', RecuOrderedDict([
            ('test', RecuOrderedDict([
                ('a', '1 + 9'),
                ('b', '2'),
                ('c', '3 and 4')
            ])),
            ('sub_main', RecuOrderedDict([
                ('sub_sub_main', RecuOrderedDict([
                    ('verb', ('line 1', 'line 2', 'line 3'))
                ]))
            ]))
        ]))
    ])


========================================
Reading merly line by line, the hard way
========================================

Let's see how the datas are roughly sent by the basic iterator of the class
``ReadBlock``.

python::
    from orpyste.data import ReadBlock

    with ReadBlock(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    ) as datas:
        for onedata in datas:
            print(
                '---',
                "mode      = <<{0}>>".format(onedata.mode),
                "data      = <<{0}>>".format(onedata.data),
                "querypath = <<{0}>>".format(onedata.querypath),
                sep = "\n"
            )


Launching in a terminal, we see the following output (for the long dictionary,
the ouput has been hand formatted).

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
    data      = <<MKOrderedDict([
                    (id=0, key='a',
                     value={'value': '1 + 9', 'nbline': 3, 'sep': '='}),
                    (id=0, key='b',
                     value={'value': '2', 'nbline': 4, 'sep': '<>'}),
                    (id=0, key='c',
                     value={'value': '3 and 4', 'nbline': 5, 'sep': '='})])>>
    querypath = <<None>>
    ---
    mode      = <<verbatim>>
    data      = <<None>>
    querypath = <<main/sub_main/sub_sub_main/verb>>
    ---
    mode      = <<verbatim>>
    data      = <<({'value': 'line 1', 'nbline': 11},
                   {'value': 'line 2', 'nbline': 12},
                   {'value': 'line 3', 'nbline': 13})>>
    querypath = <<None>>
    ---
    mode      = <<None>>
    data      = <<None>>
    querypath = <<:end:>>


The iteration still gives instances of the class ``Infos`` but with different
kinds of datas regarding to the ones obtained with the class ``Read``.

    1) For a verbatim content, a tuple of dictionaries is returned.

    2) For a key-value content, the method returns a ``MKOrderedDict``
    dictionary.


We can still ask to have easier to use datas thanks to the method ``rtu``
of the class ``data.Infos``.

...python::
    with ReadBlock(...) as datas:
        for onedata in datas:
            if onedata.isblock():
                print('--- {0} ---'.format(onedata.querypath))

            elif onedata.isdata():
                pprint(onedata.rtu)


Launched in a terminal, we obtains the following output (where the dictionary
is indeed an ordered one).

term::
    --- main/test ---
    MKOrderedDict([
        (id=0, key='a', value={'value': '1 + 9', 'nbline': 3, 'sep': '='}),
        (id=0, key='b', value={'value': '2', 'nbline': 4, 'sep': '<>'}),
        (id=0, key='c', value={'value': '3 and 4', 'nbline': 5, 'sep': '='})
    ])
    --- main/sub_main/sub_sub_main/verb ---
    [{'nbline': 11, 'value': 'line 1'},
     {'nbline': 12, 'value': 'line 2'},
     {'nbline': 13, 'value': 'line 3'}]


info::
    The number of lines in the original ¨peuf file aree kept such as to give
    fine informations to the user if one of its data is corrupted.


=============================
Looking for particular blocks
=============================

See first the documentation of the class ``Read``. Regarding to the class
``Read``, just the outputs of the class ``ReadBlock`` are different but the
way to use queries remains the same.
    """

    def __init__(
        self,
        content,
        mode,
        encoding = "utf-8"
    ):
        super().__init__(content, mode, encoding)

    def __getitem__(self, querypath):
        """
prototype::
    see = Read.__getitem__
        """
# What has to be extracted ?
        query_pattern = regexify(querypath)

# We can now extract the matching infos.
        infosfound  = False
        self._infos = None

        for oneinfo in self.walk_view:
            if oneinfo.isblock():
                self._lastmode = oneinfo.mode

                infosfound = query_pattern.search(oneinfo.querypath)

                if infosfound:
                    if self._infos is not None:
                        yield Infos(
                            mode       = self._lastmode,
                            data       = self._infos,
                            nbline     = oneinfo.nbline
                        )

                    if self._lastmode == VERBATIM:
                        self._infos = []

                    else:
                        self._infos = MKOrderedDict()

                    yield oneinfo

            elif infosfound:
                self._addblockdata(oneinfo)

        if self._infos is not None:
            yield Infos(
                mode       = oneinfo.mode,
                nbline     = oneinfo.nbline,
                data       = self._infos
            )

        self._infos    = None
        self._lastmode = None

    def _addblockdata(self, onedata):
        if self._lastmode == VERBATIM:
            nbline, line = onedata.rtu

            self._infos.append({
                NBLINE_TAG: nbline,
                VAL_TAG   : line
            })

        else:
            nbline, key, sep, val = onedata.rtu

            self._infos[key] = {
                NBLINE_TAG: nbline,
                SEP_TAG   : sep,
                VAL_TAG   : val
            }

    @property
    def flatdict(self):
        """
prototype::
    see = Infos.rtu , Infos.short_rtu , self._builddict

    return = parse.walk.MKOrderedDict ;
             an easy-to-use dictionary with keys equal to flat query paths
        """
        return self._builddict()

    def _builddict(self):
        """
This method is an abstraction used by the property-method ``self.flatdict``.
        """
        newdict = MKOrderedDict()

        for info in self:
            if info.isblock():
                lastkey = info.querypath

            elif info.isdata():
                newdict[lastkey] = info.rtu

        return newdict

    @property
    def treedict(self):
        """
prototype::
    see = self.flatdict , self._recudict

    return = parse.walk.RecuOrderedDict ;
             a dictionary using a tree like structure similar to the one of the
             blocks inside the ¨peuf file
        """
        return self._recudict(value = self.flatdict)

    def _recudict(self, value):
        if isinstance(value, MKOrderedDict):
            newdict = RecuOrderedDict()

            for key, val in value.items(noid = True):
                key = key.split("/")

                if key in newdict:
                    raise KeyError(
                        "the key << {0} >> is used at least two times".format(
                            key
                        )
                    )

                newdict[key] = self._recudict(val)

            return newdict

        return value

    def _myvalue(self, onedico):
        """
prototype::
    see = self.mydict

    arg = dict, MKOrderedDict: onedico


This method is used to only keep ¨infos wanted when a user calls the method
``mydict`` with its own settings.
        """
        # print("---", "self._removethis", self._removethis, "_myvalue(self, onedico)", onedico, sep="\n")

# Just keep what is wanted.
        for infotoremove in self._removethis:
            if infotoremove in onedico:
                del onedico[infotoremove]

# Juste one key-val association ==> only keep the value (this is a choice !)
        if len(onedico) == 1:
            for _, value in onedico.items():
                onedico = value

        return onedico

    def _specialtodict(self, oneval):
        """
prototype::
    see = self.mydict

    arg = ?: oneval


This method tries to convert recursively instances of ``MKOrderedDict`` and
``RecuOrderedDict`` to standard dictionaries.
        """
        if isinstance(oneval, MKOrderedDict):
            newdict = {}

            for (_, k), v in oneval.items():
                if k in newdict:
                    raise KeyError(
                        "the key << {0} >> is used at least two times".format(k)
                    )

                newdict[k] = self._specialtodict(v)

            return newdict

        elif isinstance(oneval, RecuOrderedDict):
            newdict = {}

            for k, v in oneval.items():
                newdict[k] = self._specialtodict(v)

            return newdict

        else:
            return oneval

    def mydict(self, kind):
        """
prototype::
    arg = str: kind ;
          this string indicates what kind of dictionary is wanted and also which
          types of ¨infos must be kept

    return = dict , MKOrderedDict , RecuOrderedDict ;
             a dictionary keeping only special ¨infos


info::
    For the kinds of dictionary you can can use ``STD_TAG = "std"``,
    ``FLAT_TAG = "flat"`` or ``TREE_TAG = "tree"``.

    To unkeep some ¨infos, you have the possibility to use
    ``NOSEP_TAG = "nosep"``, ``NONB_TAG = "nonb"`` and ``NOVAL_TAG = "noval"``.

    You can also use ``MINI_TAG = "mini"`` as a shortcut for "nosep nonb"``.

    For example, ``kind = "std nonb nosep"`` asks to try to build a standard
    dictionary without keeping separators of keys and values, and to not keep
    the numbers of lines in the original ¨peuf file.
        """
        self._settings = set()

        for param in kind.split(" "):
            param = param.strip()

            if param:
                if param in MYDICT_ALIAS_TAGS:
                    self._settings |= MYDICT_ALIAS_TAGS[param]

                else:
                    self._settings.add(param)

# Unknown setting.
        if self._settings - MYDICT_TAGS:
            raise ValueError(
                "unknown settings in {0}".format(self._settings)
            )

# Nothing to keep ?
        if NOTHING_TAGS <= self._settings:
            raise ValueError("illegal settings: nothing to keep")

# Infos to remove.
        self._removethis = []

        for option in self._settings:
            if option in NOTHING_TAGS:
                self._removethis.append(_NO_DICT_KEY[option])

# Good kind of dictionary wanted ?
        if len(MYDICT_KIND_TAGS & self._settings) == 2:
            raise ValueError("flat or tree like dict ?")

# Let's customize the values of the flat dictionary.
        newdict = MKOrderedDict()

        for (_, blockname), infos in self.flatdict.items():
# Verbatim
            if isinstance(infos, tuple):
                newdict[blockname] = tuple(
                    self._myvalue(oneval) for oneval in infos
                )

# Key-value
            else:
                newinfos = MKOrderedDict()

                for (_, key), val in infos.items():
                    newinfos[key] = self._myvalue(val)

                newdict[blockname] = newinfos

# A recursive tree like dict ?.
        if TREE_TAG in self._settings:
            newdict = self._recudict(newdict)

# Standard dict wanted ?
        if STD_TAG in self._settings:
            newdict = self._specialtodict(newdict)

# The job has been done !
        return newdict

    @property
    def forjson(self):
        """
prototype::
    see = self.flatdict, loadjson

    return = str ;
             the ¨json version of the flat dictionary version of the ¨peuf file
             analyzed


Because ¨json types are not all transposable from and to ¨python ones, the
¨json variables made here is a little ugly. The following code gives us just
after the structure used.

python::
    from orpyste.data import ReadBlock

    content = '''
    main::
        test::
            a = 1 + 9
            b <>  2

        sub_main::
            sub_sub_main::
                verb::
                    line 1
                        line 2
    '''

    with ReadBlock(
        content = content,
        mode    = {
            "container"    : ":default:",
            "keyval:: = <>": "test",
            "verbatim"     : "verb"
        }
    ) as datas:
        print(datas.forjson)


Launched in a terminal, we obtain the following output which has been hand
formatted. As you can see, we use the format json::``[key, value]`` so as
to store the keys and their coresponding value of the dictionary (as you can
see verbatim values are associated to a json::``null`` "key").

json::
    [
        [
            [0, "main/test"],
            [
                [
                    [0, "a"],
                    {"nbline": 4, "value": "1 + 9", "sep": "="}
                ],
                [
                    [0, "b"],
                    {"nbline": 5, "value": "2", "sep": "<>"}
                ]
            ]
        ],
        [
            [0, "main/sub_main/sub_sub_main/verb"],
            [
                null,
                [
                    {"nbline": 10, "value": "line 1"},
                    {"nbline": 11, "value": "    line 2"}
                ]
            ]
        ]
    ]
        """
        return dumps(self._recujson(self.flatdict))

    def _recujson(self, onevar):
        """
prototype::
    see = self.jsonify

    arg = onevar ;
          one variable to be "jsonified"

    return = ? ;
             a ¨python object that can be safely "jsonified"


This method works recursively to convert a dictionary of the datas into a
convenient ¨json version.
        """
        if isinstance(onevar, MKOrderedDict):
            jsonvar = []

            for key, val in onevar.items():
                jsonvar.append(
                    [key, self._recujson(val)]
                )

        elif isinstance(onevar, dict):
            jsonvar = onevar

        else:
            jsonvar = [None, onevar]

        return jsonvar


def _tuplize(val):
    """
prototype::
    see = _loadjson

    arg = val ;
          a ¨python variable to be recursively "tuplized"

    return = ? ;
             a ¨python variable using always tuples isntead lists


This method works recursively.
    """
    if isinstance(val, list):
        val = tuple(_tuplize(x) for x in val)

    return val


def _loadjson(jsonvar):
    """
prototype::
    see = loadjson

    arg = jsonvar ;
          one ¨json variable built by the method ``ReadBlock.jsonify``
    arg = classdict ;
          the kind of dictionary to used for the "jsonification"

    return = OrderedDict, data.RecuOrderedDict ;
             a dictionary that was built by the method ``ReadBlock.jsonify``


This method works recursively to convert a ¨json variable, built by the method
``ReadBlock.jsonify``, into a dictionary of the type ``classdict``.
    """
    if isinstance(jsonvar, dict):
        return jsonvar

    elif jsonvar[0] is None:
        return _tuplize(jsonvar[1])

    else:
        newdict = MKOrderedDict()

        for key, val in jsonvar:
            newdict[key[1]] = _loadjson(val)

        return newdict


def loadjson(jsonvar):
    """
prototype::
    see = ReadBlock.jsonify

    arg = str, file: jsonvar ;
          one ¨json variable stored in one string or in a file that was built
          by the method ``ReadBlock.jsonify``

    return = parse.walk.MKOrderedDict ;
             a flat dictionary built by the method ``ReadBlock.flatdict`` when
             producing the ¨json variable via ``ReadBlock.forjson``


This function "pythonifies" a ¨json variable built by the method ``forjson`` of
the class ``ReadBlock``.


info::
    The function will use a dictionnary ``MKOrderedDict`` implemented in the
    module ``parse.walk``.
"""
    if isinstance(jsonvar, str):
        jsonvar = loads(jsonvar)

    else:
        jsonvar = load(jsonvar)

    return _loadjson(jsonvar)
