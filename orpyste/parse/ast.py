#! /usr/bin/env python3

"""
prototype::
    date = 2015-????


This module ????

This module only contains one abstract class implementing methods needed for
parsing the ``orpyste`` files.
"""

from collections import OrderedDict, namedtuple
from pathlib import Path
import re


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


# --------- #
# -- AST -- #
# --------- #

CtxtInfos = namedtuple('CtxtInfos', ['kind', 'name', 'id_matcher'])

class AST():
    """
prototype::
    arg = ???

This class implements the methods needs to build an AST view of an
``orpyste`` file.
    """

# SOME CONSTANTS
    _CONTAINER, _EQUAL, _LINE, _MULTIEQUAL, _VERBATIM \
    = "container", "equal", "line", "multiequal", "verbatim"

    _MODES = [_CONTAINER, _EQUAL, _LINE, _MULTIEQUAL, _VERBATIM]

    _LONG_MODES = {}

    for name in _MODES:
        if name.startswith("multi"):
            _LONG_MODES["m{0}".format(name[5])] = name

        else:
            _LONG_MODES[name[0]] = name

# PATTERNS
#
# We use an ugly hack to know if something is a regex.
    RE_TYPE = type(re.compile('j'))

# CONFIGURATIONS OF THE CONTEXTS [human form]
#
# The CTXTS_CONFIGS are sorted from the first to be tested to the last one.
    _FORMATTING_KIND_CTXT = "{0}-{1}"

    INDENT, OPEN, CLOSE, AUTOCLOSE = "indent", "open", "close", "autoclose"

    CLOSED_BY_INDENT, NOTHING = range(2)

# If the two following key are not used, this will means "use all possible
# contexts inside me". The name of the context cannot look like ``:onename:``
# with double points.
    SUBCTXTS = "subcontexts"

    CTXTS_CONFIGS = OrderedDict()

# The missing ``CLOSE`` indicates an auto-close context.
    CTXTS_CONFIGS["comment-singleline"] = {
        OPEN: "^//"
    }

    CTXTS_CONFIGS["comment-multilines"] =  {
        OPEN    : "^/\*",
        CLOSE   : "\*/$",
        SUBCTXTS: NOTHING,      # This indicates no subcontexts.
    }

# ``CLOSE: CLOSED_BY_INDENT`` indicates a context using indentation for its
# content.
#
# We can use tuple to indicate several patterns, and we can also use a special
# keyword ``not::`` for negate a regex (doing this in pure regex can be very
# messy).
    CTXTS_CONFIGS["block"] = {
        OPEN: (
            "^[\d_a-zA-Z]+::$",             # TO MATCH
            "not::^[\d_a-zA-Z]+\\\\::$"     # TO NOT MATCH
        ),
        CLOSE: CLOSED_BY_INDENT
    }

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
    CTXTINFOS_EMPTYLINE = CtxtInfos(":emptyline:", "", 0)
    CTXTINFOS_CONTENT   = CtxtInfos(":content:", "", None)

    MATCHERS       = [{True: [re.compile("^$")]}]
    CTXTS_MATCHERS = [CTXTINFOS_EMPTYLINE]
    CTXTS_SUBCTXTS = {}

    id_matcher = 0
    __name2id  = {}

    for kind_ctxt in [OPEN, CLOSE]:
        for name, configs in CTXTS_CONFIGS.items():
            for kind, spec in configs.items():
# We do not keep the special keyword CLOSED_BY_INDENT.
                if kind == CLOSE and spec == CLOSED_BY_INDENT:
                    continue

# We have to take care of the use of the special keyword CLOSED_BY_INDENT.
                if kind == kind_ctxt:
                    if isinstance(spec, (str, int)):
                        spec = [spec]

                    matcher = {}

                    for s in spec:
                        if isinstance(s, str):
                            if s.startswith("not::"):
                                boolwanted = False
                                s = s[5:]

                            else:
                                boolwanted = True

                            s = re.compile(s)

                        else:
                            boolwanted = True

                        if boolwanted in matcher:
                            matcher[boolwanted].append(s)

                        else:
                            matcher[boolwanted] = [s]

                    id_matcher += 1
                    MATCHERS.append(matcher)

                    if CLOSE in configs:
                        if configs[CLOSE] == CLOSED_BY_INDENT:
                            kind = "indent"

                    else:
                        kind = AUTOCLOSE

                    CTXTS_MATCHERS.append(
                        CtxtInfos(kind, name, id_matcher)
                    )

                    __name2id[(kind, name)] = id_matcher

# SUBCONTEXTS
    for name, configs in CTXTS_CONFIGS.items():
        if SUBCTXTS in configs:
# Empty lines can appear anywhere !
            subctxts = [CTXTINFOS_EMPTYLINE.name]

            if configs[SUBCTXTS] == NOTHING:
                if (CLOSE, name) in __name2id:
                    subctxts.append(name)

            else:
                for ctxt in configs[SUBCTXTS]:
                    for kind in [OPEN, CLOSE]:
                        if (kind, ctxt) in __name2id:
                            subctxts.append(ctxt)

            CTXTS_SUBCTXTS[name] = subctxts

    __name2id = None


    def __init__(
        self,
        iotxt,
        mode,
        seps
    ):
# API attributs
        self.iotxt = iotxt
        self.mode  = mode
        self.seps  = seps

# Internal attributs
        self._nbline = 0
        self._line   = None

        self._level              = 0
        self._levels_stack       = []
        self._ctxtname_stack     = []
        self._ctxt_sbctxts_stack = []


# ---------------------------- #
# -- WALKING IN THE CONTENT -- #
# ---------------------------- #

    def nextline(self):
        """
property::
    yield = str ;
            the lines of ``self.iotxt``.
        """
        for line in self.iotxt:
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
        before = ''

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

    def match(self, text, id_matcher):
        """
property::
    arg = str: text ;
          ????
        """
# Looking for the first winning matching.
        for boolwanted, thematchers in self.MATCHERS[id_matcher].items():
            for onematcher in thematchers:
                if bool(onematcher.search(text)) != boolwanted:
                    return False

# We have a winning mathcing.
        return True

# -------------------------- #
# -- LOOKING FOR CONTEXTS -- #
# -------------------------- #

    def search_ctxts(self):
        nocontextfound = True

        for ctxtinfos in self.CTXTS_MATCHERS:
            if self._ctxt_sbctxts_stack != [] \
            and ctxtinfos.name not in self._ctxt_sbctxts_stack[-1]:
                continue

# A new context.
            if self.match(self._line, ctxtinfos.id_matcher):
                nocontextfound = False

# We can store the infos.
                self.store_ctxts(ctxtinfos)


# A new opening context.
                if ctxtinfos.kind in [self.OPEN, self.INDENT]:
                    self._ctxtname_stack.append(ctxtinfos.name)

# Do we have to use subcontexts.
                    if ctxtinfos.kind == self.OPEN \
                    and ctxtinfos.name in self.CTXTS_SUBCTXTS:
                        self._ctxt_sbctxts_stack.append(
                            self.CTXTS_SUBCTXTS[ctxtinfos.name]
                        )

# A closing context.
                elif ctxtinfos.kind == self.CLOSE:
                    if not self._ctxtname_stack:
                        raise ASTError(
                            "wrong closing context: see line #{0}".format(
                                self._nbline
                            )
                        )

                    lastctxtname = self._ctxtname_stack.pop(-1)

                    if lastctxtname != ctxtinfos.name:
                        raise ASTError(
                            "wrong closing context: " \
                            + "see line no.{0} and context \"{1}\"".format(
                                self._nbline, ctxtinfos.name
                            )
                        )

                    self._ctxt_sbctxts_stack.pop(-1)


                break

# Not a vsisble new context (be careful of indentation closing)
        if nocontextfound:
            self.store_ctxts(self.CTXTINFOS_CONTENT)


    def store_ctxts(self, ctxtinfos):
# we take care of indetation problems.
        if ctxtinfos.kind == "indent":
            if self._levels_stack:
                self._levels_stack.append(self._level)
            else:
                self._levels_stack = [self._level]

# We can store the main infos.
        print('self._levels_stack={4}\nself._ctxtname_stack = {3}\n\n{0}:[{1}]\n>>>{2}\n---'.format(
            ctxtinfos, self._level, self._line, self._ctxtname_stack, self._levels_stack
        ))


# ------------------- #
# -- BUILD THE AST -- #
# ------------------- #

    def build(self):
        """
This method builds an intermediate AST.
        """
        for line in self.nextline():
            print("nb", self._nbline)
            self._line = line
            self.manage_indent()
            self.search_ctxts()


            # self.cleanast()


# --------------------------- #
# -- STORING THE METADATAS -- #
# --------------------------- #


# --------------------------------- #
# -- NORMALIZE USER'S PARAMETERS -- #
# --------------------------------- #

#
#     def _normalize_mode(self):
#         self._mode = {}
#
#         if isinstance(self.mode, (dict, OrderedDict)):
#             self._mode["id"] = "multi"
#
#             _mode_infos = {}
#
#             for mode, blocks in self.mode.items():
#                 self._test_mode_keys(mode)
#                 self._test_mode_blocks(blocks)
#
#                 if mode == 'default':
#                     if isinstance(blocks, list):
#                         if len(blocks) != 1:
#                             raise ValueError(
#                                 'you can only use one default mode '
#                                 'in the argument ``mode``.'
#                             )
#
#                         blocks = blocks[0]
#
#                     self._mode["default"] = self.mode
#
#                 else:
#                     if isinstance(blocks, str):
#                         blocks = [blocks]
#
#                     _mode_infos[mode] = blocks
#
#             if not 'default' in self._mode:
#                 self._mode["default"] = "container"
#
#         else:
#             self._test_mode_keys(self.mode)
#
# # We must use a general behavior !
#             self._mode["id"]    = "single"
#             self._mode["default"] = self.mode
#
# # We build now easy-to-use variables.
#         self._mode["used"]  = []
#         self._mode["assos"] = {}
#
#         i = -1
#
#         for id, blocks in _mode_infos.items():
#             i += 1
#             self._mode["used"].append(id)
#
#             for b in blocks:
#                 self._mode["assos"][b] = i
#
#     def _normalize_seps(self):
#         if isinstance(self.seps, str):
#             self._seps = [self.seps]
#
#         else:
#             self._seps = sorted(
#                 self.seps,
#                 key = lambda t: -len(t)
#             )
#
#         modesused = " ".join([
#             " ".join(y)
#             for x, y in self._mode.items() if x != ":id:"
#         ])
#
#         if len(self.seps) !=1 and "equal" in modesused:
#             raise ValueError(
#                 'several separators are not allowed for equal like modes.'
#             )
