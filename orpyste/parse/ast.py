#! /usr/bin/env python3

"""
Directory : orpyste/parse
Name      : build
Version   : 2015.01
Author    : Christophe BAL
Mail      : projetmbc@gmail.com

This module only contains one abstract class implementing methods needed for
parsing the ``orpyste`` files.
"""

from collections import OrderedDict
import re

from mistool.os_use import isfile, makedir


# --------- #
# -- AST -- #
# --------- #

INDENT = 0

class AST():
    """
This abstract class implements the methods needs to build an AST view of an
``orpyste`` file.
    """

    MODES = [
        "equal" , "multiequal",
        "keyval", "multikeyval",
        "line"  , "block",
        "container"
    ]

    PATTERN_BLOCKNAME = re.compile("^[\d_a-zA-Z]+$")

# We use an ugly hack to know if something is a regex.
    RE_TYPE = type(re.compile('j'))

    def __init__(
        self,
        content  = "",
        encoding = "utf8",
        mode     = "equal",
        seps     = "=",
        patterns = None,
        strict   = False
    ):
# API attributs
        self.content  = content
        self.encoding = encoding
        self.mode     = mode
        self.seps     = seps
        self.patterns = patterns
        self.strict   = strict

# Looking for...
        self._store_in   = None
        self._tobestored = None
        self._temp_path  = None

        self._nextline = None
        self._line     = None
        self._level    = None
        self._before   = None

# Human friendly definition of the ctxts
        self.ctxts_config = None

        self.give_ctxts_config()

# Python friendly definition of the ctxts
        self._subctxts       = []
        self._actions        = []
        self._ctxts_pointers = []
        self._ctxts_stack    = []
        self._ctxt_id        = None

        self.build_actions()


# ------------- #
# -- ACTIONS -- #
# ------------- #

    def build_actions(self):
# To each method ``is_ctxt``, there must have an associated method ``add_ctxt``,
# and vice versa.
        addlike_methods = set()
        islike_methods  = set()

        for method in dir(self):
            if method.startswith("add_"):
                addlike_methods.add(method[4:])

            elif method.startswith("is_"):
                islike_methods.add(method[3:])

        if addlike_methods != islike_methods:
            message = "TTT"

            raise NotImplementedError(message)

# We have to look for the configuration of the ctxts.
        self._ctxts_pointers = []
        _id = -1

        print(self.ctxts_config)
        print()

        for onectxt in self.ctxts_config:
            _id += 1

            if isinstance(onectxt, str):
                name  = onectxt
                infos = None

            else:
                if len(onectxt) != 1:
                    raise ValueError("????")

                for name, infos in onectxt.items():
                    ...

            if name not in addlike_methods:
                raise ValueError("????")

            self._ctxts_pointers.append(name)
            self._actions.append(infos)

        print(self._ctxts_pointers)
        print(self._actions)
        exit()




        if set(methods_sorted) != addlike_methods & islike_methods:
            methods            = addlike_methods & islike_methods
            methods_sorted_set = set(methods_sorted)

            message = []

            if methods - methods_sorted_set:
                message.append("methode non rangée : {}".format(methods - methods_sorted_set))

            if methods_sorted_set - methods:
                message.append("methode manquante : {}".format(methods_sorted_set - methods))

            raise ValueError(message)

        for method in methods_sorted:
            self._actions[method] = (
                getattr(self, "is_{0}".format(method)),
                getattr(self, "add_{0}".format(method))
            )

        print(self._subctxts)
        exit()


# --------- #
# -- AST -- #
# --------- #

    def build(self):
        """
This method builds the representations
        """
        self.normalize()

        self.build_ast()

        print("self._mode")
        print(self._mode)

        print("self._ctxt_stack")
        print(self._ctxt_stack)




    def build_ast(self):
        """
This method builds an intermediate AST.
        """
        for line in self._nextline():
            self._line = line.rstrip()
            self.indentlevel()

            print('>>>', self._line)

            for id, (matcher, adder) in self._actions.items():
                self._id = id

                if matcher():
                    self.addctxt()
                    adder()
                    self._store_in()

                    break

            print()


# ---------------- #
# -- MISC TOOLS -- #
# ---------------- #

    def addctxt(self):
        self._ctxt_stack.append(self._id)

    def match(self, text):
        """
This method ???.
        """
        pattern = self.patterns[self._id]

        if pattern == None:
            return True

        else:
            return bool(pattern.search(text))


# ------------------------------ #
# -- CONFIGURING THE ctxtS -- #
# ------------------------------ #

    def give_ctxts_config(self):
        """
global logic of ctxts it is verbose but prépare chemin pour lexTex (solution de test passagère)

concordance des noms !!! via is_ et add_
        """
        self.ctxts_config = [
            "singlecomment",
            "multicomment_start_end",
            {
                "multicomment_start": {
                    "closedby": "multicomment_end",
                    "subctxts": None,
                }
            },
            {
                "block": {"closedby": INDENT}
            },
            "content"
        ]


# -------------- #
# -- COMMENTS -- #
# -------------- #

    def is_singlecomment(self):
        """
This method returns a boolean indicating if the line is a single line comment.
        """
        return self._line.startswith('//')

    def add_singlecomment(self):
        """
This method ???
        """
        self._tobestored = {
            'kind'   : "singlecomment",
            'content': self._line[2:]
        }


    def is_multicomment_start_end(self):
        """
This method returns a boolean indicating if the line is a complete multiline
comment.
        """
        return self.is_multicomment_start() and self.is_multicomment_end()

    def add_multicomment_start_end(self):
        """
This method ???
        """
        self._tobestored = {
            'kind'   : "multicomment_start_end",
            'content': self._line[2:-2]
        }

    def is_multicomment_start(self):
        """
This method returns a boolean indicating if the line is the beginning of a
multiline comment.
        """
        return self._line.startswith('/*')

    def add_multicomment_start(self):
        """
This method ???
        """
        self._tobestored = {
            'kind'   : "multicomment_start",
            'content': self._line[2:]
        }


    def is_multicomment_end(self):
        """
This method returns a boolean indicating if the line is the end of a multiline
comment.
        """
        return self._line.strip().endswith('*/')

    def add_multicomment_end(self):
        """
This method ???
        """
        self._tobestored = {
            'kind'   : "multicomment_end",
            'content': self._line[:-2]
        }


# -------------------- #
# -- STARTING BLOCK -- #
# -------------------- #

    def is_block(self):
        """
This method returns a boolean indicating if the line can be the start of a block.
        """
        line = self._line.lstrip()

        if line.endswith('::') and not line.endswith('\::'):
            if not self.match(line[:-2]):
                raise ValueError(
                    "in line {0}, illegal name << {1} >> for a block.".format(
                        self._nbline,
                        line[:-2]
                    )
                )

            else:
                return True

        else:
            return False

    def add_block(self):
        """
This method ???
        """
        self._tobestored = {
            'kind' : "block",
            'name' : self._line.lstrip()[:-2],
            'level': self._level
        }


# ------------- #
# -- CONTENT -- #
# ------------- #

# Here we have to use the metadata ``search_index`` such as to indicate to
# search first all the other ctxts which have by default a searching index
# equal to 0.

    def is_content(self):
        """
???
        """
        return True

    def add_content(self):
        """
This method ???
        """
        self.noindent()

        if self._line:
            self._tobestored = {
                'kind' : "content",
                'line' : self._line,
                'level': self._level
            }

        else:
            self._tobestored = {'kind': "emptyline"}


# ----------------- #
# -- INDENTATION -- #
# ----------------- #

    def indentlevel(self):
        """
This method returns the level of indention of a line where each tabulation is
equal to four spaces.
        """
        self._level  = 0
        self._before = ''

        for char in self._line:
            if char == ' ':
                self._before += ' '
                self._level += 1

            elif char == '\t':
                self._before += '    '
                self._level += 4

            else:
                break

        self._before = self._before[:- self._level % 4]
        self._level //= 4

    def noindent(self):
        """
This method cleans the leading indentation characters.
        """
        if self._before:
            self._line = self._before + self._line.lstrip()


# ---------------------------- #
# -- WALKING IN THE CONTENT -- #
# ---------------------------- #

    def nextline_file(self):
        """
This method is an iterator for walking line by line in a file.
        """
        with open(self.content) as f:
            self._nbline = 0

            for line in f:
                self._nbline += 1
                yield line.rstrip()

    def nextline_str(self):
        """
This method is an iterator for walking line by line in a string.
        """
        for n, line in enumerate(self.content.splitlines(), start = 1):
            self._nbline = n
            yield line.rstrip()


# ----------------------- #
# -- STORING THE DATAS -- #
# ----------------------- #

    def store_in_file(self):
        """
This method ???
        """
        RRR

    def store_in_str(self):
        """
This method ???
        """
        print('---', self._tobestored, sep="\n")


# ----------------------------------- #
# -- NORMALIZED INTERNAL ATTRIBUTS -- #
# ----------------------------------- #

    def normalize(self):
        """
This method ???
        """
# << WARNING ! >> The order is important.
        self._normalize_content()
        self._normalize_patterns()
        self._normalize_mode()
        self._normalize_seps()

    def _normalize_content(self):
        if isfile(self.content):
            self._nextline = self.nextline_file
            self._store_in = self.store_in_file

            self._temp_path = "?: file"

        else:
            self._nextline = self.nextline_str
            self._store_in = self.store_in_str

            self._temp_path = "?: str"

    def _normalize_patterns(self):
        if self.patterns == None:
            self.patterns = {
                'block': self.PATTERN_BLOCKNAME,
                'key'  : self.PATTERN_BLOCKNAME,
                'value': None
            }

        elif not isinstance(self.patterns, dict):
            self.patterns = {
                'block': self.patterns,
                'key'  : self.patterns,
                'value': None
            }

        for k, v in self.patterns.items():
            if k not in {'block', 'key', 'value'}:
                raise KeyError(
                    'you can only use the keys "block", "key", "value"'
                    'in the argument ``patterns``.'
                )

            if v == "":
                self.patterns[k] = None

# We use an ugly hack to know if something is or not a regex.
            elif v != None and not isinstance(v, self.RE_TYPE):
                raise ValueError(
                    'value of "{0}" in the dictionary ``patterns``'.format(k) \
                    + ' is neither ``None``, nor a compiled regex.'
                )

    def _test_mode_keys(self, mode):
        if mode not in self.MODES:
            raise ValueError('unknown mode << {0} >>.'.format(mode))

    def _test_mode_blocks(self, blocks):
        self._id = 'block'

        if isinstance(blocks, list):
            for b in blocks:
                self._test_mode_blocks(b)

        elif not isinstance(blocks, str):
            raise ValueError(
                'in the argument ``mode``, names of blocks must be strings.'
                ' Look at << {0} >>.'.format(blocks)
            )

        elif self.patterns['block'] \
        and not self.match(blocks):
            raise ValueError(
                'in the argument ``mode``, the name "{0}"'.format(blocks) \
                + ' does no match the regex pattern ``{0}``.'.format(
                    self.patterns['block']
                )
            )

        self._id = None

    def _normalize_mode(self):
        self._mode = {}

        if isinstance(self.mode, (dict, OrderedDict)):
            self._mode["id"] = "multi"

            _mode_infos = {}

            for mode, blocks in self.mode.items():
                self._test_mode_keys(mode)
                self._test_mode_blocks(blocks)

                if mode == 'default':
                    if isinstance(blocks, list):
                        if len(blocks) != 1:
                            raise ValueError(
                                'you can only use one default mode '
                                'in the argument ``mode``.'
                            )

                        blocks = blocks[0]

                    self._mode["default"] = self.mode

                else:
                    if isinstance(blocks, str):
                        blocks = [blocks]

                    _mode_infos[mode] = blocks

            if not 'default' in self._mode:
                self._mode["default"] = "container"

        else:
            self._test_mode_keys(self.mode)

# We must use a general behavior !
            self._mode["id"]    = "single"
            self._mode["default"] = self.mode

# We build now easy-to-use variables.
        self._mode["used"]  = []
        self._mode["assos"] = {}

        i = -1

        for id, blocks in _mode_infos.items():
            i += 1
            self._mode["used"].append(id)

            for b in blocks:
                self._mode["assos"][b] = i

    def _normalize_seps(self):
        if isinstance(self.seps, str):
            self._seps = [self.seps]

        else:
            self._seps = sorted(
                self.seps,
                key = lambda t: -len(t)
            )

        modesused = " ".join([
            " ".join(y)
            for x, y in self._mode.items() if x != ":id:"
        ])

        if len(self.seps) !=1 and "equal" in modesused:
            raise ValueError(
                'several separators are not allowed for equal like modes.'
            )
