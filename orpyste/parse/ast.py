#! /usr/bin/env python3

"""
prototype::
    date = 2017-07-27


This module contains classes so as to build an abstract syntax tree view of an
¨orpyste content. The tree view build can be stored in a file or in a string
thanks to the class ``orpyste.tools.ioview.IOView``.
"""

from collections import OrderedDict
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

# -------------------- #
# -- SAFE CONSTANTS -- #
# -------------------- #

# TAGS

SECTION_TAG = "section"

BLOCK_TAG      = "block"
MODE_TAG       = "mode"
KIND_TAG       = "kind"
SEPS_TAG       = "seps"
GRPS_FOUND_TAG = "groups_found"

NAME_TAG   = "name"
NBLINE_TAG = "nbline"

EMPTYLINE_TAG    = ":emptyline:"
VERB_CONTENT_TAG = ":verbatim:"
SPE_CONTENT_TAG  = ":content:"
CONTENT_TAG      = "content"

COMMENT_TAG = "comment"

# Modes

DEFAULT = ":default:"

MODES = CONTAINER, KEYVAL, MULTIKEYVAL, VERBATIM \
      = "container", "keyval", "multikeyval", "verbatim"

LONG_MODES = {}

for name in MODES:
    if name.startswith("multi"):
        LONG_MODES["m{0}".format(name[5])] = name

    else:
        LONG_MODES[name[0]] = name

LEGAL_BLOCK_NAME = "[\-\d_a-zA-Z]+"

# For the AST

SINGLELINE = "singleline"
MULTILINES = "multilines"

COMMENT_SINGLELINE            = "{0}-{1}".format(COMMENT_TAG, SINGLELINE)
COMMENT_MULTILINES            = "{0}-{1}".format(COMMENT_TAG, MULTILINES)
COMMENT_MULTILINES_SINGLELINE = "{0}-{1}-{2}".format(
    COMMENT_TAG, MULTILINES , SINGLELINE
)

COMMENTS_ON_JUST_ONELINE = (
    COMMENT_SINGLELINE,
    COMMENT_MULTILINES_SINGLELINE
)

MAGIC_COMMENT = "magic-comment"

OPEN      = "open"
CLOSE     = "close"
AUTOCLOSE = "autoclose"
OPENCLOSE = "openclose"


# ---------- #
# -- MODE -- #
# ---------- #

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
    have the kind ``keyval`` which is for key-value associations separated here
    by a sign ``=``, the one given after ``::``. Here are some important things
    to know.

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
    separator ``:=`` (be carefull of the points).


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
    ...     print(kind, infos, sep = "\\n    ")
    ...
    config
        {'seps': [':='], 'mode': 'keyval'}
    player
        {'seps': [':='], 'mode': 'keyval'}
    summary
        {'mode': 'verbatim'}


warning::
    Here we have not used ":default:" but we can do that (just see the following
    section). Not using ":default:" implies that only the blocks named "config",
    "player" and "summary" can be used.


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


================================
The special mode ``"illegal"``
================================

This is for illegal blocks. If you don't use this, any name not defined in the
argument ``mode`` will be interpreted as an illegal one.
    """

    def __init__(self, mode):
        self.mode = mode

# -- SPECIAL SETTER -- #
    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.build()

# -- LET'S BUILD THE AST -- #
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

# -- MODE DEFINED USING A SINGLE STRING -- #
    def _single_mode(self, mode):
        """
prototype::
    arg = str: mode ;
          this a mode defined using a single string

    return = dict ;
             either ``{"mode": mode}`` if ``mode`` is equal to ``"verbatim"``
             or ``"container"``, or ``{"mode": mode, "seps": list_of_seps}``
             where ``list_of_seps`` is a list of strings where each string is
             a legal separator (this list is sorted from the longest to the
             shortest string)
        """
        mode = mode.strip()
        i    = mode.find("::")

# verbatim or container.
        if i == -1:
            mode = LONG_MODES.get(mode, mode)

            if mode not in MODES \
            or mode in [KEYVAL, MULTIKEYVAL]:
                raise ValueError("unknown single mode ``{0}``.".format(mode))

            return {MODE_TAG: mode}

# (multi)key = value
        else:
            mode, seps = mode[:i].strip(), mode[i+2:].strip()
            mode       = LONG_MODES.get(mode, mode)

            if mode not in [KEYVAL, MULTIKEYVAL]:
                raise ValueError(
                    'unknown single mode ``{0}`` used with "::".'.format(mode)
                )

# We must first give the longest separators.
            return {
                MODE_TAG: mode,
                SEPS_TAG: sorted(
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
             ``self.dicoview`` with key corresponding to names of blocks,
             with also the special key ``":default:"``, and with values equal
             to the index in ``self.allmodes`` of the associate single mode.
        """
        self.allmodes = [self._single_mode(self.mode)]
        self.dicoview = {DEFAULT: 0}

# -- MODE DEFINED USING A DICTIONARY -- #
    def _build_from_dict(self):
        """
prototype::
    see = self._single_mode

    action = from a mode given in one dictionary, this method builds a list
             ``self.allmodes`` of all single modes and a dictionary
             ``self.dicoview`` with key corresponding to names of blocks,
             with eventually the special key ``":default:"``, and with values
             equal to the index in  ``self.allmodes`` of the associate single
             mode.
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

# -- MAGIC METHODS -- #
    def __getitem__(self, item):
        if item in self.dicoview:
            return self.allmodes[self.dicoview[item]]

        elif DEFAULT in self.dicoview:
            return self.allmodes[self.dicoview[DEFAULT]]

        raise ValueError('unknown item and no default mode.')

    def __contains__(self, item):
        if not isinstance(item, str):
            raise TypeError("a block name must be a string.")

        if not self.LEGAL_BLOCK_NAME_RE.search(item):
            raise ValueError("illegal value for a block name.")

        return (
            item in self.dicoview
            or
            DEFAULT in self.dicoview
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
               documentation of the class ``Mode``)
    arg-attr = str: encoding = "utf-8" ;
               a well named argument...


    attr = file, io.StringIO: view ;
           this attribut contains a verbose and easy to read version of the
           abstract syntax tree in either a pickle file if the argument attribut
           ``content`` is a ``pathlib.Path``, or a ``io.StringIO`` if the
           argument attribut ``content`` is a string

    method = build ;
             you have to call this method each time you must build, or rebuild,
             the abstract syntax tree


This class can build an Abstract Syntax Tree (AST) view of a merely ¨orpyste
file. We have written "merely" because here we allow some semantic illegal
¨peuf syntaxes. This will the job of ``parse.Walk`` to manage this kind of
errors among some other ones.


Here is a very simple example showing how to build the AST view and how to walk
in this view.

pyterm:
    >>> from pprint import pprint # For pretty printings of dictionaries.
    >>> from orpyste.parse.ast import AST
    >>> content = '''
    ... ==========================
    ... Section 1
    ... must be on a single line !
    ... ==========================

    ... test::
    ...     Missing a key-val first !
    ...     a = 3
    ... '''.strip()
    >>> mode = 'keyval::='
    >>> ast = AST(content = content, mode = mode)
    >>> ast.build()
    >>> for metadata in ast:
    ...     pprint(metadata)
    {'kind': 'section', 'nbline': 1, 'openclose': 'open'}
    {'content': 'Section 1', 'kind': ':verbatim:', 'nbline': 2}
    {'content': 'must be on a single line !', 'kind': ':verbatim:', 'nbline': 3}
    {'kind': 'section', 'nbline': 4, 'openclose': 'close'}
    {'kind': ':emptyline:', 'nbline': 5}
    {'groups_found': {'name': 'test'},
     'kind': 'block',
     'mode': 'keyval',
     'nbline': 6,
     'openclose': 'open'}
    {'content': {'value_in_line': 'Missing a key-val first !'},
     'kind': ':content:',
     'nbline': 7}
    {'content': {'key': 'a', 'sep': '=', 'value': '3'},
     'kind': ':content:',
     'nbline': 8}
    {'openclose': 'close', 'nbline': 8, 'kind': 'block'}


warning::
    This class does not do any semantic analysis as we can see in the example
    above where the title of the section is on two lines instead of a single
    one, and the content of the block orpyste::``test`` starts with an inline
    value instead of a key-value one. This will the job of ``parse.Walk`` to
    manage semantic problems.
    """
# CONFIGURATIONS OF THE CONTEXTS [human form]
    SPACES_PATTERN = "[ \\t]*"
    LINE_PATTERN   = "^.*$"

    KEY_GRP_PATTERN   = "(?P<key>.*?)"
    VALUE_GRP_PATTERN = "(?P<value>.*)"

# The CTXTS_CONFIGS are sorted from the first to be tested to the last one.

    CLOSED_BY_INDENT_ID, CLOSED_AT_END_ID, VERBATIM_ID = range(3)

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
    CTXTS_CONFIGS[MAGIC_COMMENT] = {
        OPEN          : "^////$",
        INFINITY_LEVEL: True,          # This allows to force the level.
        SUBCTXTS      : VERBATIM_ID    # This indicates no subcontext.
    }

    CTXTS_CONFIGS[COMMENT_SINGLELINE] = {
        OPEN          : "^//(?P<content>.*)$",
        INFINITY_LEVEL: True,
        SUBCTXTS      : VERBATIM_ID
    }

    CTXTS_CONFIGS[COMMENT_MULTILINES_SINGLELINE] = {
        OPEN          : "^/\*(?P<content>.*)\*/[ \t]*$",
        INFINITY_LEVEL: True,
        SUBCTXTS      : VERBATIM_ID
    }

    CTXTS_CONFIGS[COMMENT_MULTILINES] =  {
        OPEN            : "^/\*(?P<content>.*)$",
        CLOSE           : "^(?P<content>.*)\*/[ \t]*$",
        SUBCTXTS        : VERBATIM_ID,
        INFINITY_LEVEL  : True,
        CLOSED_AT_END_ID: True
    }

# Sections.
    CTXTS_CONFIGS[SECTION_TAG] =  {
        OPEN            : "^={2,}$",
        CLOSE           : "^={2,}$",
        SUBCTXTS        : VERBATIM_ID,
        CLOSED_AT_END_ID: False
    }

# ``CLOSE: CLOSED_BY_INDENT_ID`` indicates a context using indentation for its
# content.
#
# We can use tuple to indicate several patterns, and we can also use a special
# keyword ``not::`` for negate a regex (doing this in pure regex can be very
# messy).
    LEGAL_BLOCK_NAME_RE = re.compile("^{0}$".format(LEGAL_BLOCK_NAME))

    CTXTS_CONFIGS[BLOCK_TAG] = {
        OPEN: (
            "^{0}(?P<name>{1})::$".format(
                SPACES_PATTERN,
                LEGAL_BLOCK_NAME
            ),
            "not::^{0}{1}\\\\::$".format(
                SPACES_PATTERN,
                LEGAL_BLOCK_NAME
)
        ),
        CLOSE           : CLOSED_BY_INDENT_ID,
        CLOSED_AT_END_ID: True
    }

    def __init__(
        self,
        content,
        mode,
        encoding = "utf-8"
    ):
# User's arguments.
        self.content  = content
        self.mode     = mode
        self.encoding = encoding

# Let's build our contexts' rules.
        self.build_ctxts_rules()
        self.build_contents_rules()

# -- SPECIAL SETTERS -- #
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content      = value
            self._partial_view = IOView("list")
            self.view          = IOView("list")

        elif isinstance(value, Path):
            self._content = value

            self._partial_view = IOView(
                mode = "pickle",
                path = value.with_suffix(
                    "{0}.orpyste.partial.ast".format(value.suffix)
                )
            )

            self.view = IOView(
                mode = "pickle",
                path = value.with_suffix(
                    "{0}.orpyste.ast".format(value.suffix)
                )
            )

        else:
            raise TypeError("invalid type for the attribut ``content``.")

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = Mode(value)

# -- INTERNAL CONTEXTS' RULES -- #
    def build_ctxts_rules(self):
        """
prototype::
    action = this method builds ¨python none human lists and dictionaries used
             to build an intermediate abstract syntax tree of the contexts
             which are either opening or closing blocks or comments, or empty
             lines, or lines of contents (you can breath now).
             This will be the job of ``self.build_contents_rules`` to take care
             of lines of contents.
        """
# MATCHERS FOR THE CONTEXTS [the E.T. experience] ;-)
#
# We build ¨python none human list for research with the following constraints.
#
#     1) We stop as soon as we find a winning matching.
#     2) If a an opening context has been found just before, we have to test
#        first its associated closing context which can be either a pattern or #        an indentation closing.
#        Then we look for "all" the other opening and then closing contexts.
#     3) If no open context has been found just before, we test first "all" the
#        open contexts and then "all" the close ones.
#     4) We have to take care of subcontexts.
#     5) We store the regex objects in a list (think about the subcontexts).
#
# << Warning ! >> We add a matcher for empty line at the very beginning because
# we want to keep them but we have also have to skip them when searching for
# contexts. So easy... :-(
        self.MATCHERS = [{
            True:                   # Boolean wanted.
            [re.compile("^$")]      # List of regexes to test.
        }]

        self.CLOSING_ID_FROM_OPENING = {}

        self.CTXTINFOS_EMPTYLINE = CtxtInfos(
            kind       = EMPTYLINE_TAG,
            id_matcher = 0    # See ``self.MATCHERS``.
        )

        self.CTXTINFOS_CONTENT = CtxtInfos(kind = SPE_CONTENT_TAG)

        self.CTXTS_MATCHERS = [self.CTXTINFOS_EMPTYLINE]

        self.CTXTS_KINDS_SUBCTXTS = {}

        self.INFINITY                    = float('inf')
        self.CTXTS_KINDS_WITH_INF_LEVELS = set()

        self.CTXTS_KINDS_CLOSED_AT_END = set()

        id_matcher = len(self.MATCHERS) - 1
        name2id    = {}

        for openclose in [OPEN, CLOSE]:
            for kind, configs in self.CTXTS_CONFIGS.items():
                if openclose in configs:
                    spec = configs[openclose]

# We do not keep the special keyword CLOSED_BY_INDENT_ID.
                    if openclose == CLOSE \
                    and spec == self.CLOSED_BY_INDENT_ID:
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

                    if CLOSE in configs:
                        if configs[CLOSE] == self.CLOSED_BY_INDENT_ID:
                            indented = True

                        else:
                            indented = False

                            self.CLOSING_ID_FROM_OPENING[kind] = id_matcher

                    else:
                        _openclose = AUTOCLOSE
                        indented    = False

                    if configs.get(self.CLOSED_AT_END_ID, False):
                        self.CTXTS_KINDS_CLOSED_AT_END.add(kind)

                    verbatim = (
                        self.SUBCTXTS in configs
                        and
                        configs[self.SUBCTXTS] == self.VERBATIM_ID
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

                if configs[self.SUBCTXTS] == self.VERBATIM_ID:
                    if (CLOSE, kind) in name2id:
                        subctxts.append((CLOSE, kind))

                else:
                    for kind in configs[self.SUBCTXTS]:
                        for openclose in [OPEN, CLOSE]:
                            if (openclose, kind) in name2id:
                                subctxts.append((openclose, kind))

                self.CTXTS_KINDS_SUBCTXTS[kind] = subctxts

# -- INTERNAL CONTENTS' RULES -- #
    def build_contents_rules(self):
        """
prototype::
    action = this method builds ¨python none human lists and dictionaries used
             to build from the intermediate abstract syntax tree of the
             contexts the final abstract syntax tree where the lines of contents
             have been analyzed.
        """
# Configurations of the patterns for datas in contexts
        self.CONTENTS_MATCHERS = {}

        id_matcher = len(self.MATCHERS)

# For the "verbatim" mode.
        self.MATCHERS.append({True: [re.compile("^(?P<value_in_line>.*)$")]})
        id_verbatim = id_matcher

# Let's work !
        for ctxt, configs in self.mode.items():
# "keyval" or "multikeyval" modes.
            if configs[MODE_TAG] in [KEYVAL, MULTIKEYVAL]:
# We must take care of separators with several characters, and we also have to
# escape special characters.
                seps = []

                for onesep in configs[SEPS_TAG]:
                    if len(onesep) != 1:
                        onesep = "({0})".format(re.escape(onesep))

                    else:
                        onesep = re.escape(onesep)

                    seps.append(onesep)

                pattern = re.compile(
                    "{spaces}{key}{spaces}(?P<sep>{seps}){spaces}{value}"
                        .format(
                            spaces = self.SPACES_PATTERN,
                            key    = self.KEY_GRP_PATTERN,
                            value  = self.VALUE_GRP_PATTERN,
                            seps   = "|".join(seps)
                        )
                )

                self.MATCHERS.append({True: [pattern]})
                id_matcher += 1

# Do we have regex groups ?
                regex_grps = [x for x in pattern.groupindex]

                self.CONTENTS_MATCHERS[ctxt] = ContentInfos(
                    mode       = configs[MODE_TAG],
                    id_matcher = [id_matcher, id_verbatim],
                    regex_grps = regex_grps,
                )

# "verbatim" and "container" modes.
            elif configs[MODE_TAG] in [VERBATIM, CONTAINER]:
                self.CONTENTS_MATCHERS[ctxt] = ContentInfos(
                    mode       = configs[MODE_TAG],
                    id_matcher = id_verbatim
                )

# Mode not implemented.
            else:
                raise ValueError(
                    "BUG to report : mode ``{0}`` not implemented".format(
                        configs[MODE_TAG]
                    )
                )

# -- WALKING IN THE CONTENT -- #
    def nextline(self):
        """
property::
    yield = str ;
            each line of ``self.content``.
        """
        if isinstance(self._content, str):
            for line in StringIO(self._content):
                self._nbline += 1
                yield line.rstrip()

        else:
            with self._content.open(
                mode     = "r",
                encoding = self.encoding
            ) as peuffile:
                for line in peuffile:
                    self._nbline += 1
                    yield line.rstrip()

# -- INDENTATION -- #
    def manage_indent(self):
        """
property::
    action = the level of indention is calculated and the leading indentation
             of ``self._line`` is removed (one tabulation is exactly equal to
             four spaces).
        """
        if self._line \
        and self._level != self.INFINITY:
            self._level = 0

            for char in self._line:
                if char == ' ':
                    self._level += 1

                elif char == '\t':
                    self._level += 4

                else:
                    break

            self._oldline = self._line

            self._line = " "*(self._level % 4) + self._oldline.lstrip()
            self._level //= 4

# -- REGEXES -- #
    def match(self, text, infos):
        """
property::
    arg = str: text ;
          this string is a text where we look for some metadatas (a context or
          a data content)
    arg = CtxtInfos, ContentInfos: infos ;
          this indicates which matcher must be used to test a matching on the
          argument ``text``

    return = bool ;
             ``True`` or ``False`` whether something matches or not
        """
        for oneid in infos.id_matcher:
            match_found        = True
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

                if match_found is False:
                    break

            if match_found is True:
                break

# We have a winning matching or not.
        return match_found

# -- BUILD THE AST -- #
    def build(self):
        """
prototype::
    action = this method calls all the methods needed so as to build the
             abstract syntax tree.
        """
# Internal attributs
        self._nbline = 0
        self._line   = None

        self._verbatim = False

        self._level        = 0
        self._levels_stack = []

        self._ctxts_opened_stack = []
        self._ctxt_sbctxts_stack = []

# Intermediate AST only for contexts.
        with self._partial_view:
            for self._line in self.nextline():
                self.search_ctxts()

            self.close_ctxt_at_end()

# Final AST with datas in contents.
        with self.view:
            self.search_contents()

# The partial view is not usefull in the disk.
        self._partial_view.remove()

# -- LOOKING FOR CONTEXTS -- #
    def search_ctxts(self):
        """
prototype::
    action = this method looks for contexts which can be either opening or
             closing blocks or comments, or empty lines, or lines of contents.
        """
        ctxtfound            = False
        mustclose_otherctxts = False

# Do we close the last context opened ?
        if self._ctxts_opened_stack:
            closeby_id = self.CLOSING_ID_FROM_OPENING.get(
                self._ctxts_opened_stack[-1].kind,
                None
            )

            if closeby_id:
                ctxtinfos = self.CTXTS_MATCHERS[closeby_id]

                if self.match(self._line, ctxtinfos):
                    ctxtfound = True

# Other contexts must be searched.
        if not ctxtfound:
            for ctxtinfos in self.CTXTS_MATCHERS:
# Not a subcontext ?
                if self._ctxt_sbctxts_stack \
                and (
                    ctxtinfos.openclose,
                    ctxtinfos.kind
                ) not in self._ctxt_sbctxts_stack[-1]:
                    continue

# A new context found.
                if self.match(self._line, ctxtinfos):
                    ctxtfound            = True
                    mustclose_otherctxts = bool(ctxtinfos.openclose == OPEN)
                    break

# Now that a context has been found, or not, we can manage indentation.
        self.manage_indent()

# Unvisible new context (be careful of indentation closing)
        if not ctxtfound:
            ctxtinfos            = self.CTXTINFOS_CONTENT
            mustclose_otherctxts = True

# Level can be forced to infinity.
        if ctxtinfos.kind in self.CTXTS_KINDS_WITH_INF_LEVELS \
        and ctxtinfos.openclose != AUTOCLOSE:
            self._level = self.INFINITY

# Close previous contexts.
        if mustclose_otherctxts:
            self.close_indented_ctxts(ctxtinfos)

# Add an opening context in the stack.
        if ctxtinfos.openclose == OPEN:
            self._ctxts_opened_stack.append(ctxtinfos)

# Do we have to use subcontexts ?
            if ctxtinfos.kind in self.CTXTS_KINDS_SUBCTXTS:
                self._ctxt_sbctxts_stack.append(
                    self.CTXTS_KINDS_SUBCTXTS[ctxtinfos.kind]
                )

# A closing context.
        elif ctxtinfos.openclose == CLOSE:
            if not self._ctxts_opened_stack:
                raise ASTError(
                    "wrong closing context: see line #{0}".format(
                        self._nbline
                    )
                )

            lastctxt = self._ctxts_opened_stack.pop(-1)

            if lastctxt.kind != ctxtinfos.kind:
                raise ASTError(
                    "wrong closing context: " \
                    + "see line no.{0} and context \"{1}\"".format(
                        self._nbline, ctxtinfos.kind
                    )
                )

            self._ctxt_sbctxts_stack.pop(-1)
            self._levels_stack.pop(-1)
            self._level = 0

# We can store the new and eventually close some old contexts.
        # # --- UGLY DEBUG --- #
        # print("AST -->", ctxtinfos)
        self.store_one_ctxt(ctxtinfos)

    def must_close_indented_ctxt(self):
        """
prototype::
    return = bool ;
             ``True`` or ``False`` whether we have to close or not the actual
             context due to the indentation
        """
        return self._levels_stack and self._level <= self._levels_stack[-1]

    def close_indented_ctxts(self, ctxtinfos):
        """
prototype::
    action = this method closes all contexts that use indentation for their
             content.
        """
# Sections close all blocks !
        if ctxtinfos.kind == SECTION_TAG:
            if ctxtinfos.openclose == OPEN:
                while self._ctxts_opened_stack:
                    self._levels_stack.pop(-1)

                    lastctxt = self._ctxts_opened_stack.pop(-1)

                    if not lastctxt.indented:
                        break

                    self.store_one_ctxt(
                        CtxtInfos(
                            kind      = lastctxt.kind,
                            openclose = CLOSE
                        ),
                        not_add_groups_alone = False
                    )

            self._ctxts_opened_stack = self._levels_stack = []

# Not a section. What can't close an indented contexts ?
#     * Verbatim contents
#     * Empty lines
#     * Autoclosed context
#     * Comments on a single line
        elif self._ctxts_opened_stack \
        and not self._ctxts_opened_stack[-1].verbatim \
        and ctxtinfos != self.CTXTINFOS_EMPTYLINE \
        and ctxtinfos.openclose != AUTOCLOSE \
        and ctxtinfos.kind not in COMMENTS_ON_JUST_ONELINE:
            if self._levels_stack \
            and self._levels_stack[-1] != self.INFINITY:
                while self.must_close_indented_ctxt():
                    self._levels_stack.pop(-1)

                    lastctxt = self._ctxts_opened_stack.pop(-1)

                    self.store_one_ctxt(
                        CtxtInfos(
                            kind      = lastctxt.kind,
                            openclose = CLOSE
                        ),
                        not_add_groups_alone = False
                    )

# We update the stack of levels.
        if ctxtinfos.openclose == OPEN:
            if self._levels_stack \
            and self._level != self._levels_stack[-1]:
                self._levels_stack.append(self._level)

            else:
                self._levels_stack = [self._level]

# Autoclose context with infinite level do not change the levels !
        elif ctxtinfos.openclose == AUTOCLOSE \
        and self._levels_stack \
        and self._level == self.INFINITY:
            self._level = self._levels_stack[-1]

# Close context with infinite level need to clean the stack of levels !
        elif ctxtinfos.openclose == CLOSE \
        and self._levels_stack \
        and self._level == self.INFINITY:
            self._levels_stack.pop(-1)

            if self._levels_stack:
                self._level = self._levels_stack[-1]

            else:
                self._level = 0

# Ugly patch !
        if self._level == self.INFINITY:
            self._level = 0

    def close_ctxt_at_end(self):
        """
prototype::
    action = this method closes all contexts than can be closed automatically
             at the very end of the ¨orpyste file
        """
        while self._ctxts_opened_stack:
            lastctxt_kind = self._ctxts_opened_stack.pop(-1).kind

            if lastctxt_kind not in self.CTXTS_KINDS_CLOSED_AT_END:
                raise ASTError(
                    "unclosed context: " \
                    + "see line no.{0} and context \"{1}\"".format(
                        self._nbline, lastctxt_kind
                    )
                )

            self.store_one_ctxt(
                CtxtInfos(kind = lastctxt_kind, openclose = CLOSE)
            )

# -- LOOKING FOR DATAS IN CONTENTS -- #
    def search_contents(self):
        """
prototype::
    action = this method looks for datas in contents regarding the mode of the
             blocks.
        """
        _defaultmatcher     = self.CONTENTS_MATCHERS.get(DEFAULT, None)
        self._matcherstack  = []
        self._nb_emptylines = 0

        for onemeta in self.next_partial_meta():
            # --- IMPORTANT : UGLY DEBUG --- #
            # print("AST >>>", onemeta, "\n" + " "*7, self._levels_stack);continue

# The big messe of empty lines in verbatim content.
# One new block.
            if onemeta[KIND_TAG] == BLOCK_TAG:
                if onemeta[OPENCLOSE] == OPEN:
# Preceding block must be a container !
                    if not self.last_block_is_container():
                        raise ASTError(
                            "last block not a container, see line nb.{0}" \
                                .format(onemeta[NBLINE_TAG])
                        )

                    matcher = self.CONTENTS_MATCHERS.get(
                        onemeta[GRPS_FOUND_TAG][NAME_TAG],
                        _defaultmatcher
                    )

                    if not matcher:
                        raise ASTError(
                            "last block << {0} >> is illegal, see line nb.{1}" \
                                .format(
                                    onemeta[GRPS_FOUND_TAG][NAME_TAG],
                                    onemeta[NBLINE_TAG]
                                )
                        )

# We must know the mode used by this block.
                    onemeta[MODE_TAG] = matcher.mode

                    self._matcherstack.append(matcher)

                else:
                    self._matcherstack.pop(-1)

# Some content.
            elif onemeta[KIND_TAG] == SPE_CONTENT_TAG:
                if not self._matcherstack:
                    raise ASTError(
                        "no block before, see line nb.{0}".format(
                            onemeta[NBLINE_TAG]
                        )
                    )

# A good content ?
                if self.match(onemeta[CONTENT_TAG], self._matcherstack[-1]):
# We have to remove escaped character ``\::``.
                    if 'value_in_line' in self._groups_found:
                        value_in_line = self._groups_found['value_in_line']

                        if value_in_line.endswith("\::"):
                            value_in_line = value_in_line[:-3] + "::"
                            self._groups_found['value_in_line'] = value_in_line

                    onemeta[CONTENT_TAG] = self._groups_found

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
            return self._matcherstack[-1].mode == CONTAINER

        return True

# -- STORING THE METADATAS -- #
    def add(self, metadatas):
        self.view.write(metadatas)

    def add_partial(self, metadatas):
        self._partial_view.write(metadatas)

    def next_partial_meta(self):
        for x in self._partial_view:
            yield x

    def store_one_ctxt(self, ctxtinfos, not_add_groups_alone = True):
        metadatas = {
            KIND_TAG  : ctxtinfos.kind,
            NBLINE_TAG: self._nbline,
        }

        if ctxtinfos.openclose:
            if ctxtinfos.openclose == AUTOCLOSE:
                metadatas[OPENCLOSE] = OPEN

            else:
                metadatas[OPENCLOSE] = ctxtinfos.openclose

        if ctxtinfos.verbatim:
            verbatimstart = self._groups_found.get(CONTENT_TAG, None)

            if verbatimstart is not None:
                del self._groups_found[CONTENT_TAG]

        else:
            verbatimstart = None

        if not_add_groups_alone and self._groups_found:
            metadatas[GRPS_FOUND_TAG] = self._groups_found

        if verbatimstart is not None:
            verbatimstart = {
                KIND_TAG   : VERB_CONTENT_TAG,
                NBLINE_TAG : self._nbline,
                CONTENT_TAG: verbatimstart,
            }

# We have to keep extra indentations !
        if ctxtinfos.kind == SPE_CONTENT_TAG:
            if self._ctxts_opened_stack[-1].kind[:7] == "comment":
                extra      = ""
                self._line = self._oldline

            elif self._levels_stack \
            and self._levels_stack[-1] != self.INFINITY \
            and self._level != self.INFINITY:
                if self._levels_stack \
                and self._level > self._levels_stack[-1]:
                    extra = " "*4*(self._level - self._levels_stack[-1] - 1)

                else:
                    extra = " "*self._level

            else:
                extra = ""


            metadatas[CONTENT_TAG] = "{0}{1}".format(extra, self._line)

            if self._verbatim:
                metadatas[KIND_TAG] = VERB_CONTENT_TAG

# We must change emtylines in comment to a verbatim empty content.
        elif ctxtinfos.kind == EMPTYLINE_TAG and self._verbatim:
            metadatas[KIND_TAG]    = VERB_CONTENT_TAG
            metadatas[CONTENT_TAG] = ""

        if verbatimstart and ctxtinfos.openclose == CLOSE:
            metadatas, verbatimstart = verbatimstart, metadatas

        if metadatas:
            self.add_partial(metadatas)

        if ctxtinfos.verbatim:
            if verbatimstart:
                self.add_partial(verbatimstart)

            if ctxtinfos.openclose == OPEN:
                self._verbatim = True

            elif ctxtinfos.openclose == CLOSE:
                self._verbatim = False

        if ctxtinfos.openclose == AUTOCLOSE:
            new_metadatas = {k: v for k, v in metadatas.items()}
            new_metadatas[OPENCLOSE] = CLOSE
            self.add_partial(new_metadatas)

# -- MAGIC METHOD -- #
    def __iter__(self):
        for x in self.view:
            yield x
