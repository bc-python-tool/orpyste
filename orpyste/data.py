#! /usr/bin/env python3

"""
Directory : orpyste
Name      : data
Version   : 2015.01
Author    : Christophe BAL
Mail      : projetmbc@gmail.com

This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.
"""

from orpyste.parse import ast, pyit


class Read():
    """
NOUVEL API !!!!
    ---> gestion intelligente de path et content
    ---> pattern

All the parsing job done by ``build.BaseClass``



-------------------
The classical modes
-------------------

Suppose that you have the following ``orpyste`` file (sorry for the lake of
originality).

orpyste::
    // Two single line comments.
    // The start of the comment must be at the very beginning of the line !

    game_rules::
        Play !
        Try to win.
        Win or let go.

    /* The start of the comment must be at the very beginning of the line !
     *
     * One comment on several lines...
     */

    names_of_levels::
        easy
        medium
        hard

    player_1::
        age   = 18
        sexe  = male
        score = 1874
        alias = Super Mario

    player_2::
        age   = 24
        sex   = female
        score = 2007
        alias = Sonic


Let suppose that the preceding file has the path path::``user/myFile.txt``. Then
we can extract informations by using the following code.

python::
    import orpyste

    infos = orpyste.data.Reader(
        path = "user/myFile.txt",
        mode = {
            'block': "game_rules",
            'line' : "names_of_levels",
            'equal': ["player_1", "player_2"]
        }
    )


Using the preceding code, then ``infos.datas`` will be the following ordered
dictionary.

python::
    {
        'games_rules'    : "Play !\\nTry to win.\\nWin or let go.",
        'names_of_levels': ["easy", "medium", "hard"],
        'player_1': {
            'age'  : '18',
            'sexe' : 'male',
            'score': '1874',
            'alias': 'Super Mario'
        }
        'player_2': {
            'age'  : '24',
            'sexe' : 'female',
            'score': '2007',
            'alias': 'Sonic'
        },
    }


You can also work directly with string like in the following example which has
the same effect as the preceding one.

python::
    import orpyste

    mycontent = '''
    game_rules::
        Play !
        Try to win.
        Win or let go.

    names_of_levels::
        easy
        medium
        hard

    player_1::
        age   = 18
        sexe  = male
        score = 1874
        alias = Super Mario

    player_2::
        age   = 24
        sex   = female
        score = 2007
        alias = Sonic
    '''

    infos = orpyste.data.Reader(
        content = mycontent,
        mode    = {
            'block': "game_rules",
            'line' : "names_of_levels",
            'equal': ["player_1", "player_2"]
        }
    )


If you want to have a finer control for the block and line contents, just use
the attribut ``dictnbline``. For the preceding code, ``infos.datas_nblines`` is
equal to following ordered dictionary where the content are replaced by uplets
``(Number of the line, Content)``.

python::
    {
        'game_rules'     : (3, 'Play !\\nTry to win.\\nWin or let go.'),
        'names_of_levels': [(8, 'easy'), (9, 'medium'), (10, 'hard')],
        'player_1': {
            'age'  : '18',
            'sexe' : 'male',
            'score': '1874',
            'alias': 'Super Mario'
        }
        'player_2': {
            'age'  : '24',
            'sexe' : 'female',
            'score': '2007',
            'alias': 'Sonic'
        },
    }


-----------------------------
The special mode ``"keyval"``
-----------------------------

Let finish with a very special mode with the following ``orpyste`` file where we
want to use ``<==>``, ``==>``, ``=`` like ``key-value`` separators.

orpyste::
    logic::
        a <==> b
        x ==> y

    constraint::
        i     = j
        alpha <= beta


Let suppose that the preceding file has the path path::``user/myFile.txt``. Then
we can extract informations by using the following code.

python::
    import orpyste

    infos = orpyste.data.Reader(
        path = "user/myFile.txt",
        mode = "keyval",
        sep = ["<==>", "==>", "=", "<="]
    )


Using the preceding code, then ``infos.dict`` will be the following ordered
dictionary.

python::
    {
        'logic': {
            '<==>': {'a': "b"},
            '==>' : {'x': "y"}
        },
        'constraint': {
            '=' : {'i': "j"},
            '<=': {'alpha': "beta"}
        }
    }


-------------
The arguments
-------------

This class uses the following variables.

    1) ``content`` is one content to analyse. You can use this variable or the
    variable ``path``.

    2) ``path`` is the complete path of the file to read. You can use this
    variable or the variable ``content``.

    3) ``encoding`` is the encoding of the file using the standard python name
    for encoding. By default, its value is the string ``"utf8"``.

    4) ``mode`` indicates how the informations have been stored in the file to
    read. The possible values are the next ones.

        a) ``"equal"`` is for informations stored line by line with key-value
        syntax ``key = value`` in every blocks to analyse. This is the default
        value of the variable ``mode``.

        info::
            Newlines are allowed inside values. To use one sign ``=`` in one
            value, you have to escape at least the first sign ``=`` via ``\=``.
            Be carefull that each empty line will be translated to a single
            space.

        b) ``"keyval"`` extends the mode ``"equal"`` by allowing to use
        different separators defined in the variable ``sep`` (see below).

        c) There are also two modes ``"multiequal"`` and ``"multikeyval"`` that
        extend ``"equal"`` and ``"keyval"`` by allowing to use several times the
        same name for keys.

        d) ``"line"`` is for informations stored line by line without any
        special syntax in each line in the blocks to analyse.

        e) ``"block"`` is for information stored in a whole paragraph made of
        several lines in the blocks to analyse.

        f) We can also use one of the preceding modes for different blocks. In
        that case, we simply use one dictionary like in the following example
        where the special mode ``"container"`` is for blocks that contains other
        blocks. Indeed, you can just use only the keys you need.

        python::
            mode = {
                'default'    : the default mode,
                'equal'      : [names of the blocks],
                'multiequal' : [names of the blocks],
                'keyval'     : [names of the blocks],
                'multikeyval': [names of the blocks],
                'line'       : [names of the blocks],
                'block'      : [names of the blocks],
                'container'  : [names of the blocks]
            }

        If you only need one name of block, you don't have to put in one single
        value list. Just give its name in a string.

        If you don't define the value associated to the key ``'default'`` then
        the value ``"container"`` will be use by default.

    5) ``sep`` indicates which text(s) is used to separate keys and values for
    the modes ``"equal"``, ``"multiequal"``, ``"keyval"`` and ``"multikeyval"``.
    You can use a single string or a list of strings.

    By default, ``sep = "="`` which is justified for the use of the classical
    modes ``"equal"`` and ``"multiequal"``.

    warning::
        You can't use a list of separators with one of the modes ``"equal"`` and
        ``"multiequal"``.

    """

    AST  = ast.AST
    PYIT = pyit.AST2PY


    def __init__(
        self,
        content  = "",
        encoding = "utf8",
        mode     = "equal",
        seps     = "=",
        patterns = None,
        strict   = False
    ):
# Public attributs
        self.content  = content
        self.encoding = encoding
        self.mode     = mode
        self.seps     = seps
        self.patterns = patterns
        self.strict   = strict

# Internal attributs



# --------------------- #
# -- BUILD THE DATAS -- #
# --------------------- #

#     @property
#     def datas(self):
#         """
# This property like method gives ???
#         """
#         if self._datas == None:
#             self.build()
#
#         return self._datas

    def build(self):
# Making of an AST view.
        _AST = self.AST(
            content  = self.content,
            encoding = self.encoding,
            mode     = self.mode,
            seps     = self.seps,
            patterns = self.patterns,
            strict   = self.strict
        )

        _AST.build()


# Transforming the AST view to a more friendly format.
