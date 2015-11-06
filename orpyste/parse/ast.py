#! /usr/bin/env python3

"""
prototype::
    date = 2015-07-03


This module contains classes so as to build an abstract syntax tree view of
¨orpyste content which is stored in a file or in a string.
"""


from collections import OrderedDict, defaultdict
from io import StringIO
from pathlib import Path
import re

from orpyste.tools.ioview import IOView

# ------------------------- #
# -- FOR ERRORS TO RAISE -- #
# ------------------------- #

class ASTError(ValueError):
    """
prototype::
    type = cls ;
           base class for errors specific to the Abstract Syntax Tree.
    """
    pass


# ---------- #
# -- MODE -- #
# ---------- #

# MODES
MODES = CONTAINER, KEYVAL, MULTIKEYVAL, VERBATIM \
      = "container", "keyval", "multikeyval", "verbatim"

LONG_MODES = {}

for name in MODES:
    if name.startswith("multi"):
        LONG_MODES["m{0}".format(name[5])] = name

    else:
        LONG_MODES[name[0]] = name

LEGAL_BLOCK_NAME = re.compile("^[\d_a-zA-Z]+$")


class Mode():
    """
prototype::
    see = AST

    arg-attr = str, dict: mode ;
               an ¨orpyste mode that can use different kinds of syntax

    action = this class is used by the class ``AST`` so as to know the mode of
             a block


==================================
Mode defined using a single string
==================================

If all the blocks are of the same kind, you just have to give it using a
single string like in the following example. You can see that the class
``Mode`` has some useful magic properties similar to the ones of a dictionary.
We will talk later of the very special block name ``":default:"`` that gives
the default kind of block.

pyterm::
    >>> from orpyste.parse.ast import Mode
    >>> mode = Mode("keyval::=")
    >>> for kind, infos in mode.items():
    ...     print(kind, infos, sep = "\n    ")
    ...
    :default:
        {'mode': 'keyval', 'seps': ['=']}
    >>> print(mode[":default:"])
    {'mode': 'keyval', 'seps': ['=']}
    >>> print(":default:" in mode)
    True
    >>> print("test" in mode)
    True
    >>> print(4 in mode)
    Traceback (most recent call last):
    [...]
    TypeError: a block name must be a string.
    >>> print("@test" in mode)
    Traceback (most recent call last):
    [...]
    ValueError: illegal value for a block name.


A mode defined within a single string must follow the rules below.

    1) ``"verbatim"`` indicates a line by line content where no line has to be
    analyzed.

    2) ``"keyval::="`` is made of two parts separated by ``::``. Before we
    have a kind ``keyval`` which is for key-value associations separated here
    by a sign ``=``, the one given after ``::``. Some important things to
    know.

        a) With this kind of mode, a key can be used only one time in the same
        block.

        b) You can use different separators. Just give all of them separated
        by one space. For example, ``"keyval::==> <== <==>"`` allows to use
        ``==>``, ``<==`` or ``<==>``.

        c) All spaces are cleaned : for example, ``"   keyval ::   ==>   <==
        <==>   "`` and ``"keyval::==> <== <==>"`` define the same mode.

    3) Instead of ``"keyval"``, you can use ``"multikeyval"`` if you want to
    allow the use of the same key several times in the same block.

    4) ``"container"`` is a special kind for blocks that can only contains
    other blocks.


info::
    Internally the class uses the attributs ``dicoview`` and ``allmodes``
    which are in our example the following dictionary and list respectively.

    ...pyterm::
        >>> print(mode.dicoview)
        {':default:': 0}
        >>> print(mode.allmodes)
        [{'mode': 'keyval', 'seps': ['=']}]


===============================
Mode defined using a dictionary
===============================

Let's suppose that we want to use the following kinds of blocks.

    * The block ``summary`` is a verbatim one containing a summary. What a
    surprise !

    * The blocks ``player`` and ``config`` are key-value blocks with only the
    separator ``:=``.


The code below shows how to do that. This is very simple has you can see (we
have used a space to allow a better readability). Just note that the keys are
single string definition of a mode, as we have seen them in the first section,
and values are either a single string for just one block, or a list of blocks.

pyterm::
    >>> from orpyste.parse.ast import Mode
    >>> mode = Mode({
    ...     "keyval:: :=": ["player", "config"],
    ...     "verbatim"   : "summary"
    ... })
    >>> for kind, infos in mode.items():
    ...     print(kind, infos, sep = "\n    ")
    ...
    config
        {'seps': [':='], 'mode': 'keyval'}
    player
        {'seps': [':='], 'mode': 'keyval'}
    summary
        {'mode': 'verbatim'}


warning::
    Here we have not used ":default:", but we can do it (just see the following
    section). This implies that only the blocks named "config", "player" or
    "summary" can be used.


================================
About the use of ``":default:"``
================================

The following code shows the very special status of ``":default:"``. As you
can see any block whose name has not been used when defining the modes will
be allways seen as a default block. **Be aware of that !**

pyterm::
    >>> from orpyste.parse.ast import Mode
    >>> mode = Mode({
    ...     "keyval:: :=": ["player", "config"],
    ...     "verbatim"   : "summary",
    ...     "container"  : ":default:"
    ... })
    >>> print("unknown" in mode)
    True
    >>> print(mode["unknown"])
    {'mode': 'container'}
    """

    def __init__(self, mode):
        self.mode = mode


# -------------------- #
# -- SPECIAL SETTER -- #
# -------------------- #

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.build()


# ------------------------- #
# -- LET'S BUILD THE AST -- #
# ------------------------- #

    def build(self):
        """
prototype::
    see = self._build_from_str , self._build_from_dict

    action = this method calls the good method that will build a standard
             version of the modes (some checkings are done)
        """
# One string.
        if isinstance(self.mode, str):
            self._build_from_str()

# One dictionary.
        elif isinstance(self.mode, (dict, OrderedDict)):
            self._build_from_dict()

# Unsupported type.
        else:
            raise TypeError("illegal type for the argument ``mode``.")


# ---------------------------------------- #
# -- MODE DEFINED USING A SINGLE STRING -- #
# ---------------------------------------- #

    def _single_mode(self, mode):
        """
prototype::
    arg = str: mode ;
          this a mode defined using a single string

    return = dict ;
             either ``{"mode": mode}`` if mode is equal to ``"verbatim"`` or
             ``"container"``, or ``{"mode": mode, "seps": list_of_seps}`` where
             ``list_of_seps`` is a list of strings where each string is a legal
             separator (this list is sorted from the longest to the shortest
             string)
        """
        mode = mode.strip()
        i    = mode.find("::")

# verbatim or container.
        if i == -1:
            mode = LONG_MODES.get(mode, mode)

            if mode not in MODES \
            or mode in [KEYVAL, MULTIKEYVAL]:
                raise ValueError("unknown single mode ``{0}``.".format(mode))

            return {"mode": mode}

# (multi)key = value
        else:
            mode, seps = mode[:i].strip(), mode[i+2:].strip()
            mode       = LONG_MODES.get(mode, mode)

            if mode not in [KEYVAL, MULTIKEYVAL]:
                raise ValueError('unknown single mode used with "::".')

# We must first give the longest separators.
            return {
                "mode": mode,
                "seps": sorted(
                    [s.strip() for s in seps.split(" ")],
                    key = lambda s: -len(s)
                )
            }


    def _build_from_str(self):
        """
prototype::
    see = self._single_mode

    action = from a mode given in one string, this method builds a list
             ``self.allmodes`` of all single modes and a dictionary
             ``self.dicoview`` with key corresponding to names of blocks, with
             also the spacial key ``":default:"``, and with values equal to the
             index in  ``self.allmodes`` of the associate single mode.
        """
        self.allmodes = [self._single_mode(self.mode)]
        self.dicoview = {":default:": 0}


# ------------------------------------- #
# -- MODE DEFINED USING A DICTIONARY -- #
# ------------------------------------- #

    def _build_from_dict(self):
        """
prototype::
    see = self._single_mode

    action = from a mode given in one dictionary, this method builds a list
             ``self.allmodes`` of all single modes and a dictionary
             ``self.dicoview`` with key corresponding to names of blocks,
             with also the spacial key ``":default:"``, and with values equal
             to the index in  ``self.allmodes`` of the associate single mode.
        """
        self.dicoview = {}
        self.allmodes = []
        id_mode       = -1

        for mode, blocks in self.mode.items():
            mode = self._single_mode(mode)

            self.allmodes.append(mode)
            id_mode += 1

            if isinstance(blocks, str):
                self.dicoview[blocks] = id_mode

            else:
                for oneblock in blocks:
                    self.dicoview[oneblock] = id_mode


# ------------------- #
# -- MAGIC METHODS -- #
# ------------------- #

    def __getitem__(self, item):
        if item in self.dicoview:
            return self.allmodes[self.dicoview[item]]

        elif ":default:" in self.dicoview:
            return self.allmodes[self.dicoview[":default:"]]

        raise ValueError('unknown item and no default mode.')


    def __contains__(self, item):
        if not isinstance(item, str):
            raise TypeError("a block name must be a string.")

        if not LEGAL_BLOCK_NAME.search(item):
            raise ValueError("illegal value for a block name.")

        return (
            item in self.dicoview
            or
            ":default:" in self.dicoview
        )


    def items(self):
        for block, id_block in self.dicoview.items():
            yield block, self.allmodes[id_block]


# --------- #
# -- AST -- #
# --------- #

class _Common():
    """
prototype::
    see = CtxtInfos, ContentInfos

    action = this class only implements the magic method ``__repr__`` for both
             of the classes ``CtxtInfos`` and ``ContentInfos``
    """

    def __repr__(self):
        return "{0}({1})".format(
            self.__class__.__name__,
            ", ".join([
                "{0}={1}".format(k, repr(self.__dict__[k]))
                for k in sorted(self.__dict__.keys())
            ])
        )


class CtxtInfos(_Common):
    """
prototype::
    see = AST

    arg-attr = str: kind
    arg-attr = int, list(int): id_matcher = -1
    arg-attr = bool: indented = False
    arg-attr = str: openclose = ""
    arg-attr = list(str): regex_grps = []
    arg-attr = bool: verbatim = False

    action = this class is simply an object view used by ``AST`` to store some
             informations.
    """

    def __init__(
        self,
        kind,
        id_matcher = -1,
        indented   = False,
        openclose  = "",
        regex_grps = [],
        verbatim   = False
    ):
        self.kind       = kind
        self.openclose  = openclose
        self.indented   = indented
        self.regex_grps = regex_grps
        self.verbatim   = verbatim

        if isinstance(id_matcher, int):
            id_matcher = [id_matcher]

        self.id_matcher = id_matcher


class ContentInfos(_Common):
    """
prototype::
    see = AST

    arg-attr = str: mode
    arg-attr = int, list(int): id_matcher
    arg-attr = list(str): regex_grps = []

    action = this class is simply an object view used by ``AST`` to store some
             informations.
    """

    def __init__(
        self,
        mode,
        id_matcher,
        regex_grps = []
    ):
        self.mode       = mode
        self.regex_grps = regex_grps

        if isinstance(id_matcher, int):
            id_matcher = [id_matcher]

        self.id_matcher = id_matcher


class AST():
    """
prototype::
    see = Mode, CtxtInfos, ContentInfos

    arg-attr = pathlib.Path, str: content ;
               ``content`` can be an instance of the class ``pathlib.Path``,
               that is a file given using its path, or ``content`` can be a
               string with all the content to be analyzed (see the attribut
               ``view``)
    arg-attr = str, dict: mode ;
               an ¨orpyste mode that can use different kinds of syntax (see the
               documentation of the class ``Mode`` for examples)

    attr = file, io.StringIO: view ;
           this attribut contains an easy to read version of the abstract syntax
           tree in either a pickle file if the argument attribut ``content`` is
           a ``pathlib.Path``, or a ``io.StringIO`` if the argument attribut
           ``content`` is a string respectively

    method = build ;
             you have to call this method each time you must build or rebuild
             the abstract syntax tree


This class can build an Abstract Syntax Tree (AST) view of a merely ¨orpyste
file: here we allow some semantic illegal ¨peuf syntaxes. This will the job of
``parse.Walk`` to check if there are this kind of errors among other ones.
Here is a very simple example showing how to build the AST view and how to walk
in this view.

pyterm:
    >>> from orpyste.parse.ast import AST
    >>> content = '''
    ... test::
    ...     Missing a key-val first !
    ...     a = 3
    ... '''.strip()
    >>> mode = {
    ...     'container': ":default:",
    ...     'keyval::=': "test",
    ...     'verbatim' : "summary"
    ... }
    >>> ast = AST(content = content, mode = mode)
    >>> ast.build()
    >>> from pprint import pprint # For a pretty prints of the dictionaries.
    >>> for metadata in ast:
    ...     pprint(metadata)
    {'groups_found': {'name': 'test'},
     'kind': 'block',
     'line': 1,
     'mode': 'keyval',
     'openclose': 'open'}
    {'content': {'value_in_line': 'Missing a key-val first !'},
     'kind': ':content:',
     'line': 2}
    {'content': {'key': 'a', 'sep': '=', 'value': '3'},
     'kind': ':content:',
     'line': 3}
    {'kind': 'block', 'line': 3, 'openclose': 'close'}


warning::
    This class does not do any semantic analysis as we can see in the example
    where the content of the block orpyste::``test`` starts with an inline value
    instead of a key-value one.
    """
# CONFIGURATIONS OF THE CONTEXTS [human form]
#
# The CTXTS_CONFIGS are sorted from the first to be tested to the last one.
    OPEN, CLOSE, AUTOCLOSE = "open", "close", "autoclose"

    CLOSED_BY_INDENT, CLOSED_AT_END, VERBATIM, RECURSIVE = range(4)

# If the two following key are not used, this will means "use all possible
# contexts inside me". The name of the context cannot look like ``:onename:``
# with double points.
    SUBCTXTS       = "subcontexts"
    INFINITY_LEVEL = "inf-level"

    CTXTS_CONFIGS = OrderedDict()

# The missing ``CLOSE`` indicates an auto-close context.
#
# << Warning ! >> The group name ``content`` indicates to put matching in a
# content line like context.
    CTXTS_CONFIGS["comment-singleline"] = {
        OPEN          : "^//(?P<content>.*)$",
        INFINITY_LEVEL: True,       # This allows to force the level.
        SUBCTXTS      : VERBATIM    # This indicates no subcontext.
    }

    CTXTS_CONFIGS["comment-multilines-singleline"] = {
        OPEN          : "^/\*(?P<content>.*)\*/$",
        INFINITY_LEVEL: True,
        SUBCTXTS      : VERBATIM
    }

    CTXTS_CONFIGS["comment-multilines"] =  {
        OPEN          : "^/\*(?P<content>.*)$",
        CLOSE         : "^(?P<content>.*)\*/$",
        SUBCTXTS      : VERBATIM,
        INFINITY_LEVEL: True,
        CLOSED_AT_END : True
    }

# ``CLOSE: CLOSED_BY_INDENT`` indicates a context using indentation for its
# content.
#
# We can use tuple to indicate several patterns, and we can also use a special
# keyword ``not::`` for negate a regex (doing this in pure regex can be very
# messy).
    CTXTS_CONFIGS["block"] = {
        OPEN: (
            "^(?P<name>[\d_a-zA-Z]+)::$",
            "not::^[\d_a-zA-Z]+\\\\::$"
        ),
        CLOSE        : CLOSED_BY_INDENT,
        CLOSED_AT_END: True
    }


    def __init__(
        self,
        content,
        mode
    ):
# User's arguments.
        self.content = content
        self.mode    = mode

# Let's build our contexts' rules.
        self.build_ctxts_rules()
        self.build_contents_rules()


# --------------------- #
# -- SPECIAL SETTERS -- #
# --------------------- #

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content      = StringIO(value)
            self._partial_view = IOView("list")
            self.view          = IOView("list")

        elif isinstance(value, Path):
            self._content = value

            self._partial_view = IOView(
                mode = "pickle",
                path = value / ".partial.ast"
            )

            self.view = IOView(
                mode = "pickle",
                path = value / ".ast"
            )

        else:
            raise TypeError("invalid type for the attribut ``content``.")


    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = Mode(value)


# ------------------------------ #
# -- INTERNAL CONTEXTS' RULES -- #
# ------------------------------ #

    def build_ctxts_rules(self):
        """
prototype::
    action = this method builds ¨python none human lists and dictionaries used
             to build an intermediate abstract syntax tree of the contexts which
             are either opening or closing blocks or comments, or empty lines,
             or lines of contents.
             This will be the job of ``self.build_contents_rules`` to take care
             of lines of contents.
        """
# MATCHERS FOR THE CONTEXTS [E.T. form]
#
# We build ¨python none human list for research with the following constraints.
#
#     1) We test all the open contexts and then the close ones.
#     2) We stop as soon as we find a winning matching.
#     3) We have to take care of subcontexts.
#     4) We store the regex objects in a list (think about the subcontexts).
#
# << Warning ! >> We add a matcher for empty line at the very beginning because
# we want to keep them but we have also to skip them when searching for
# contexts.
        self.CTXTINFOS_EMPTYLINE = CtxtInfos(
            kind       = ":emptyline:",
            id_matcher = 0
        )

        self.CTXTINFOS_CONTENT = CtxtInfos(kind = ":content:")

        self.MATCHERS       = [{True: [re.compile("^$")]}]
        self.CTXTS_MATCHERS = [self.CTXTINFOS_EMPTYLINE]

        self.CTXTS_KINDS_SUBCTXTS = {}

        self.INFINITY                    = float('inf')
        self.CTXTS_KINDS_WITH_INF_LEVELS = set()

        self.CTXTS_KINDS_CLOSED_AT_END = set()

        id_matcher = 0
        name2id    = {}

        for openclose in [self.OPEN, self.CLOSE]:
            for kind, configs in self.CTXTS_CONFIGS.items():
                if openclose in configs:
                    spec = configs[openclose]

# We do not keep the special keyword CLOSED_BY_INDENT.
                    if openclose == self.CLOSE \
                    and spec == self.CLOSED_BY_INDENT:
                        continue

# We manage other cases.
                    if isinstance(spec, (str, int)):
                        spec = [spec]

                    matcher    = {}
                    regex_grps = []

# A regex pattern.
                    for s in spec:
                        if s.startswith("not::"):
                            boolwanted = False
                            s = s[5:]

                        else:
                            boolwanted = True

                        pattern = re.compile(s)

# Do we have regex groups ?
                        regex_grps += [x for x in pattern.groupindex]

# We add a new regex.
                        if boolwanted in matcher:
                            matcher[boolwanted].append(pattern)

                        else:
                            matcher[boolwanted] = [pattern]

                    id_matcher += 1
                    self.MATCHERS.append(matcher)

                    _openclose = openclose

                    if self.CLOSE in configs:
                        if configs[self.CLOSE] == self.CLOSED_BY_INDENT:
                            indented = True

                        else:
                            indented = False

                    else:
                        _openclose = self.AUTOCLOSE
                        indented    = False

                    if configs.get(self.CLOSED_AT_END, False):
                        self.CTXTS_KINDS_CLOSED_AT_END.add(kind)

                    verbatim = (
                        self.SUBCTXTS in configs
                        and
                        configs[self.SUBCTXTS] == self.VERBATIM
                    )

                    self.CTXTS_MATCHERS.append(
                        CtxtInfos(
                            kind       = kind,
                            openclose  = _openclose,
                            indented   = indented,
                            id_matcher = id_matcher,
                            regex_grps = regex_grps,
                            verbatim   = verbatim
                        )
                    )

                    name2id[(openclose, kind)] = id_matcher

# SUBCONTEXTS AND CONTEXT'S LEVEL
        for kind, configs in self.CTXTS_CONFIGS.items():
            if self.INFINITY_LEVEL in configs:
                self.CTXTS_KINDS_WITH_INF_LEVELS.add(kind)

            if self.SUBCTXTS in configs:
# Empty lines can appear anywhere !
                subctxts = [(
                    self.CTXTINFOS_EMPTYLINE.openclose,
                    self.CTXTINFOS_EMPTYLINE.kind
                )]

                if configs[self.SUBCTXTS] == self.VERBATIM:
                    if (self.CLOSE, kind) in name2id:
                        subctxts.append((self.CLOSE, kind))

                else:
                    for kind in configs[self.SUBCTXTS]:
                        for openclose in [self.OPEN, self.CLOSE]:
                            if (openclose, kind) in name2id:
                                subctxts.append((openclose, kind))

                self.CTXTS_KINDS_SUBCTXTS[kind] = subctxts


# ------------------------------ #
# -- INTERNAL CONTENTS' RULES -- #
# ------------------------------ #

    def build_contents_rules(self):
        """
prototype::
    action = this method builds ¨python none human lists and dictionaries used
             to build from the intermediate abstract syntax tree of the
             contexts the final abstract syntax tree where the lines of contents
             have been analyzed.
        """
# Configurations of the patterns for datas in contexts
        SPACES_PATTERN = "[ \\t]*"
        LINE_PATTERN   = "^.*$"

        KEY_GRP_PATTERN   = "(?P<key>[\d_a-zA-Z]+)"
        VALUE_GRP_PATTERN = "(?P<value>.*)"

        self.CONTENTS_MATCHERS = {}

        id_matcher = len(self.MATCHERS)

# For the "verbatim" mode.
        self.MATCHERS.append({True: [re.compile("^(?P<value_in_line>.*)$")]})
        id_verbatim = id_matcher

# Let's work !
        for ctxt, configs in self.mode.items():
# "keyval" or "multikeyval" modes.
            if configs["mode"] in ["keyval", "multikeyval"]:
# We must take care of separators with several characters, and we also have to
# escape special characters.
                seps = []

                for onesep in configs["seps"]:
                    if len(onesep) != 1:
                        onesep = "({0})".format(re.escape(onesep))

                    else:
                        onesep = re.escape(onesep)

                    seps.append(onesep)

                pattern = re.compile(
                    "{spaces}{key}{spaces}(?P<sep>{seps}){spaces}{value}" \
                        .format(
                            spaces = SPACES_PATTERN,
                            key    = KEY_GRP_PATTERN,
                            value  = VALUE_GRP_PATTERN,
                            seps   = "|".join(seps)
                        )
                )

                self.MATCHERS.append({True: [pattern]})
                id_matcher += 1

# Do we have regex groups ?
                regex_grps = [x for x in pattern.groupindex]

                self.CONTENTS_MATCHERS[ctxt] = ContentInfos(
                    mode       = configs["mode"],
                    id_matcher = [id_matcher, id_verbatim],
                    regex_grps = regex_grps,
                )

# "verbatim" en "container" modes.
            elif configs["mode"] in ["verbatim", "container"]:
                self.CONTENTS_MATCHERS[ctxt] = ContentInfos(
                    mode       = configs["mode"],
                    id_matcher = id_verbatim
                )

# Mode not implemented.
            else:
                raise ValueError(
                    "BUG to report : mode ``{0}`` not implemented".format(
                        configs["mode"]
                    )
                )

# ---------------------------- #
# -- WALKING IN THE CONTENT -- #
# ---------------------------- #

    def nextline(self):
        """
property::
    yield = str ;
            each line of ``self.content``.
        """
        for line in self.content:
            self._nbline += 1
            yield line.rstrip()


# ----------------- #
# -- INDENTATION -- #
# ----------------- #

    def manage_indent(self):
        """
property::
    action = the level of indention is calculated and the leading indentation
             of ``self._line`` is removed (one tabulation is equal to four
             spaces).
        """
        if self._level == self.INFINITY:
            return None

        if self._line:
            before      = ''
            self._level = 0

            for char in self._line:
                if char == ' ':
                    self._level += 1
                    before      += ' '

                elif char == '\t':
                    self._level += 4
                    before      += '    '

                else:
                    break

            self._line    = before[:- self._level % 4] + self._line.lstrip()
            self._level //= 4


# ------------- #
# -- REGEXES -- #
# ------------- #

    def match(self, text, infos):
        """
property::
    arg = str: text ;
          this string is a text where we look for some metadatas (a context or a
          data content)
    arg = CtxtInfos, ContentInfos: infos ;
          this indicates which matcher must be used to test a matching on the
          argument ``text``

    return = bool ;
             ``True`` or ``False`` whether something matches or not
        """
        for oneid in infos.id_matcher:
            match_found = True
            self._groups_found = {}

# Looking for the first winning matching.
            for boolwanted, thematchers \
            in self.MATCHERS[oneid].items():
                for onematcher in thematchers:
                    search = onematcher.search(text)

                    if bool(search) != boolwanted:
                        match_found = False
                        break

# Do we have groups to stored ?
                    elif search:
                        self._groups_found.update(search.groupdict())

                if match_found == False:
                    break

            if match_found == True:
                break

# We have a winning mathcing.
        return match_found


# ------------------- #
# -- BUILD THE AST -- #
# ------------------- #

    def build(self):
        """
prototype::
    action = this method calls all the methods needed so as to build the
             abstract syntax tree.
        """
# Internal attributs
        self._nbline = 0
        self._line   = None

        self._level              = 0
        self._levels_stack       = []
        self._ctxts_stack        = []
        self._ctxt_sbctxts_stack = []

# Intermediate AST only for contexts.
        with self._partial_view:
            self._verbatim = False

            for line in self.nextline():
                self._line = line
                self.manage_indent()
                self.search_ctxts()

            self.close_ctxt_at_end()


# Final AST with datas in contents.
        with self.view:
            self.search_contents()


# The partial view is not usefull in the idsk.
        self._partial_view.remove()


# -------------------------- #
# -- LOOKING FOR CONTEXTS -- #
# -------------------------- #

    def search_ctxts(self):
        """
prototype::
    action = this method looks for contexts which can be either opening or
             closing blocks or comments, or empty lines, or lines of contents.
        """
        nocontextfound = True

        for ctxtinfos in self.CTXTS_MATCHERS:
# Not a subcontext ?
            if self._ctxt_sbctxts_stack \
            and (
                ctxtinfos.openclose,
                ctxtinfos.kind
            ) not in self._ctxt_sbctxts_stack[-1]:
                continue

# A new context.
            if self.match(self._line, ctxtinfos):
                nocontextfound = False

# Level can be forced to infinity.
                if ctxtinfos.kind in self.CTXTS_KINDS_WITH_INF_LEVELS \
                and ctxtinfos.openclose != self.AUTOCLOSE:
                    self._level = self.INFINITY

# A new opening context.
                if ctxtinfos.openclose == self.OPEN:
                    self._ctxts_stack.append(ctxtinfos)

# Do we have to use subcontexts ?
                    if ctxtinfos.kind in self.CTXTS_KINDS_SUBCTXTS:
                        self._ctxt_sbctxts_stack.append(
                            self.CTXTS_KINDS_SUBCTXTS[ctxtinfos.kind]
                        )

# A closing context.
                elif ctxtinfos.openclose == self.CLOSE:
                    if not self._ctxts_stack:
                        raise ASTError(
                            "wrong closing context: see line #{0}".format(
                                self._nbline
                            )
                        )

                    lastctxt = self._ctxts_stack.pop(-1)

                    if lastctxt.kind != ctxtinfos.kind:
                        raise ASTError(
                            "wrong closing context: " \
                            + "see line no.{0} and context \"{1}\"".format(
                                self._nbline, ctxtinfos.kind
                            )
                        )

                    self._ctxt_sbctxts_stack.pop(-1)

                break

# Not a visible new context (be careful of indentation closing)
        if nocontextfound:
            ctxtinfos = self.CTXTINFOS_CONTENT

# We can store the new and eventually close some old contexts.
        self.close_indented_ctxts(ctxtinfos)
        self.store_one_ctxt(ctxtinfos)


    def must_close_indented_ctxt(self):
        """
prototype::
    return = bool ;
             ``True`` or ``False`` whether we have to close or not the actual
             context due to the indentation
        """
        if self._levels_stack:
            return self._level <= self._levels_stack[-1]

        return False


    def close_indented_ctxts(self, ctxtinfos):
        """
prototype::
    action = this method closes all contexts that use indentation for their
             content.
        """
# Empty lines, autoclosed context or context with infinite level are the only
# contexts that can't close an indented context.
        if ctxtinfos != self.CTXTINFOS_EMPTYLINE \
        and ctxtinfos.openclose != self.AUTOCLOSE \
        and self._level != self.INFINITY:
            if self._levels_stack \
            and self._levels_stack[-1] != self.INFINITY:
                while self.must_close_indented_ctxt():
                    self._levels_stack.pop(-1)

                    lastctxt = self._ctxts_stack.pop(-1)

                    self.store_one_ctxt(
                        CtxtInfos(
                            kind                 = lastctxt.kind,
                            openclose            = self.CLOSE),
                            not_add_groups_alone = False
                    )

# We update the stack of levels.
        if ctxtinfos.openclose == self.OPEN:
            if self._levels_stack \
            and self._level != self._levels_stack[-1]:
                self._levels_stack.append(self._level)

            else:
                self._levels_stack = [self._level]

# Autoclose context with infinite level do not change the levels !
        elif ctxtinfos.openclose == self.AUTOCLOSE \
        and self._levels_stack \
        and self._level == self.INFINITY:
            self._level = self._levels_stack[-1]

# Close context with infinite level need to clean the stack of levels !
        elif ctxtinfos.openclose == self.CLOSE \
        and self._levels_stack \
        and self._level == self.INFINITY:
            self._levels_stack.pop(-1)

            if self._levels_stack:
                self._level = self._levels_stack[-1]

            else:
                self._level = 0


    def close_ctxt_at_end(self):
        """
prototype::
    action = this method closes all contexts than can be closed automatically at
             the very end of the ¨orpyste file
        """
        while self._ctxts_stack:
            lastctxt_kind = self._ctxts_stack.pop(-1).kind

            if lastctxt_kind not in self.CTXTS_KINDS_CLOSED_AT_END:
                raise ASTError(
                    "unclosed context: " \
                    + "see line no.{0} and context \"{1}\"".format(
                        self._nbline, lastctxt_kind
                    )
                )

            self.store_one_ctxt(
                CtxtInfos(kind = lastctxt_kind, openclose = self.CLOSE)
            )


# ----------------------------------- #
# -- LOOKING FOR DATAS IN CONTENTS -- #
# ----------------------------------- #

    def search_contents(self):
        """
prototype::
    action = this method looks for datas in contents regarding the mode of the
             blocks.
        """
        self._defaultmatcher = self.CONTENTS_MATCHERS[":default:"]
        self._matcherstack   = []

        for onemeta in self.next_partial_meta():
# One new block.
            if onemeta['kind'] == "block":
                if onemeta['openclose'] == "open":
# Preceding block must be a container !
                    if not self.last_block_is_container():
                        raise ASTError("lastblock not a container, see line nb.{0}".format(onemeta['line']))

                    matcher = self.CONTENTS_MATCHERS.get(
                        onemeta['groups_found']['name'],
                        self._defaultmatcher
                    )

# We must know the mode used by this block.
                    onemeta['mode'] = matcher.mode

                    self._matcherstack.append(matcher)

                else:
                    self._matcherstack.pop(-1)

# Some content.
            elif onemeta['kind'] == ":content:":
                if not self._matcherstack:
                    raise ASTError(
                        "no block before, see line nb.{0}".format(
                            onemeta['line']
                        )
                    )

# A good content ?
                if self.match(onemeta['content'], self._matcherstack[-1]):
                    onemeta['content'] = self._groups_found

# We can add the metadatas.
            self.add(onemeta)


    def last_block_is_container(self):
        """
prototype::
    return = bool ;
             ``True`` or ``False`` whether the last block opened is or not a
             container
        """
        if self._matcherstack:
            return self._matcherstack[-1].mode == "container"

        return True


# --------------------------- #
# -- STORING THE METADATAS -- #
# --------------------------- #

    def add(self, metadatas):
        self.view.write(metadatas)


    def add_partial(self, metadatas):
        self._partial_view.write(metadatas)


    def next_partial_meta(self):
        for x in self._partial_view:
            yield x


    def store_one_ctxt(self, ctxtinfos, not_add_groups_alone = True):
        metadatas = {
            "kind": ctxtinfos.kind,
            "line": self._nbline,
        }

        if ctxtinfos.openclose:
            if ctxtinfos.openclose == self.AUTOCLOSE:
                metadatas["openclose"] = self.OPEN

            else:
                metadatas["openclose"] = ctxtinfos.openclose

        if ctxtinfos.verbatim:
            verbatim = self._groups_found.get("content", None)

            if verbatim != None:
                del self._groups_found["content"]

        else:
            verbatim = None

        if not_add_groups_alone and self._groups_found:
            metadatas["groups_found"] = self._groups_found

        if verbatim != None:
            verbatim = {
                "kind"   : ":verbatim:",
                "line"   : self._nbline,
                "content": verbatim,
            }

# We have to keep extra indentations !
        if ctxtinfos.kind == ":content:":
            if self._levels_stack \
            and self._levels_stack[-1] != self.INFINITY \
            and self._level != self.INFINITY:
                if self._levels_stack \
                and self._level > self._levels_stack[-1]:
                    extra = " "*4*(self._level - self._levels_stack[-1] - 1)

                else:
                    extra = " "*self._level

            else:
                extra = ""

            metadatas["content"] = "{0}{1}".format(extra, self._line)

            if self._verbatim:
                metadatas["kind"] = ":verbatim:"

# We must change emtylines in comment to a verbatim empty content.
        elif ctxtinfos.kind == ":emptyline:" and self._verbatim:
            metadatas["kind"]    = ":verbatim:"
            metadatas["content"] = ""

        if ctxtinfos.openclose == self.CLOSE:
            metadatas, verbatim = verbatim, metadatas

        if metadatas:
            self.add_partial(metadatas)

        if verbatim:
            self.add_partial(verbatim)

            if ctxtinfos.openclose == self.OPEN:
                self._verbatim = True

            elif ctxtinfos.openclose == self.CLOSE:
                self._verbatim = False

        if ctxtinfos.openclose == self.AUTOCLOSE:
            new_metadatas = {k: v for k,v in metadatas.items()}
            new_metadatas["openclose"] = self.CLOSE
            self.add_partial(new_metadatas)


# ------------------- #
# -- MAGIC METHODS -- #
# ------------------- #

    def __iter__(self):
        for x in self.view:
            yield x
