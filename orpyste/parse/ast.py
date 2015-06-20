#! /usr/bin/env python3

"""
prototype::
    date = 2015-06-????


This module contains  ????


 one class that build an Abstract Syntax Tree view of
a file or a StringIO with a content using the ``peuf`` specifications.
"""

from collections import OrderedDict, defaultdict
from io import StringIO
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


# ---------- #
# -- MODE -- #
# ---------- #

class Mode():
    """
    arg = Mode: mode = Mode("keyval::=") ;

    passer par une classe via un mode simple de config
        : config ;
        str: mode = "keyval::=" with {keyval} in self.IN_CTXTS
                                                or in self.LONG_IN_CTXTS ;


==================================
Mode defined using a single string
==================================

si string c'est que pour des blocs de niveau 1 tus du même type

keyval        onekey=...
multikeyval   multikey=...
line          line by line content
verbatim      single verbaitm string !!!!

= ou plusieurs opérateurs sans esapce commme dans
multikeyval:: = < >

espace de début pour lisibiliré uniquement



==================================
Mode defined using a single string
==================================


          dict comme avant toujours possible car pratqiue au jour le jour

          config via classe dédié pour cas complexe ou typage des données si besoin`

          Z !!!! Par contre on doit passer par classe dédiée qu el'on met en fait ici
    """
# MODES
    CONTAINER, KEYVAL, MULTIKEYVAL, VERBATIM \
    = "container", "keyval", "multikeyval", "verbatim"

    MODES      = [CONTAINER, KEYVAL, MULTIKEYVAL, VERBATIM]
    LONG_MODES = {}

    for name in MODES:
        if name.startswith("multi"):
            LONG_MODES["m{0}".format(name[5])] = name

        else:
            LONG_MODES[name[0]] = name


    def __init__(self, mode):
        self.mode = mode

        self.build()


    def build(self):
# One string.
        if isinstance(self.mode, str):
            self._build_from_str()

# One dictionary.
        elif isinstance(self.mode, (dict, OrderedDict)):
            self._build_from_dict()

# A file or a StringIO.
        else:
            self._build_from_iotxt()


# ---------------------------------------- #
# -- MODE DEFINED USING A SINGLE STRING -- #
# ---------------------------------------- #

    def _build_from_str(self):
        """
only block of indent level 0 with same kind of datas
        """
        self.dicoview = {":default:": self._single_mode(self.mode)}


    def _single_mode(self, text):
        """

keyval        onekey=...
multikeyval   multikey=...
line          line by line content
verbatim      single verbaitm string !!!!
        """
        text = text.strip()
        i    = text.find("::")

# key = value ? in :
        if i != -1:
            mode, seps = text[:i], text[i+2:]
            mode       = mode.strip()
            mode       = self.LONG_MODES.get(mode, mode)

            if mode not in [self.KEYVAL, self.MULTIKEYVAL]:
                raise ValueError("unknown single mode used with \"::\".")

# We must first give the longest separators.
            return {
                "mode": mode,
                "seps": sorted(
                    [s.strip() for s in seps.split(" ")],
                    key = lambda s: -len(s))
            }

# Line or verbatim !
        mode = self.LONG_MODES.get(text, text)

        if mode not in self.MODES:
            raise ValueError("unknown single mode.")

        return {"mode": mode}


# ------------------------------------- #
# -- MODE DEFINED USING A DICTIONARY -- #
# ------------------------------------- #

    def _build_from_dict(self):
        TODO_FROM_DICT


# ------------------------------------- #
# -- MODE DEFINED USING THE FILE API -- #
# ------------------------------------- #

    def _build_from_iotxt(self):
        TODO_FROM_IOTXT



# --------- #
# -- AST -- #
# --------- #

class CtxtInfos():
    """"

        name          = "",
        kind          = "",
        openclose     = "",
        indented      = False,
        closed_at_end = False,
        id_matcher    = -1


        name,                 # For name of a users block.
        kind,                 # "block", "comment-singleline", ...
        oc,                   # "open" or "close"
        indent,               # Indentation is used for the content.
        closed_at_end,        # For blocks to automatically close at the end.
        id_matcher            # Matchers are stored separately.
    """
    def __init__(
        self,
        kind       = "",
        openclose  = "",
        id_matcher = -1,
        indented   = False,
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


    def __repr__(self):
        return "CtxtInfos({0})".format(
            ", ".join([
                "{0}={1}".format(k, repr(self.__dict__[k]))
                for k in sorted(self.__dict__.keys())
            ])
        )


class ContentInfos():
    """"
    ???
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


    def __repr__(self):
        return "ContentInfos({0})".format(
            ", ".join([
                "{0}={1}".format(k, repr(self.__dict__[k]))
                for k in sorted(self.__dict__.keys())
            ])
        )

# Inutile MAIS garder pour tutos car TB !!!
    def __eq__(self, other):
        if not isinstance(other, ContentInfos):
            raise TypeError("comparison impossible.")

        for k in self.__dict__.keys():
            if self.__dict__[k] != other.__getattribute__(k):
                return False

        return True


class AST():
    """
prototype::
    arg = ???

This class implements the methods needs to build an AST view of an
merely ``orpyste`` file : here we allow the use of content and block at the same level. This will the job of data.Read to check if there are this kind of errors among other ones.
    """
# STORING MODES
    STORE_TEMP, STORE_MEMORY = "temp", "memory"
    STORING_MODES            = [STORE_TEMP, STORE_MEMORY]

# SHORTNAMES FOR STORING MODES
    LONG_STORING_MODES = {x[0]:x for x in STORING_MODES}

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

# pb des commentaires qui ne ferment rien en fait car intégré dans un ocntenu , à définir dasn les sépcifications !!!!


# The missing ``CLOSE`` indicates an auto-close context.
    CTXTS_CONFIGS["comment-singleline"] = {
        OPEN          : "^//(?P<content>.*)$",
        INFINITY_LEVEL: True,        # This allows to force the level.
        SUBCTXTS      : VERBATIM
    }

# << Warning ! >> If name = content indictae to put matching in a content line like
    CTXTS_CONFIGS["comment-multilines"] =  {
        OPEN          : "^/\*(?P<content>.*)$",
        CLOSE         : "^(?P<content>.*)\*/$",
        SUBCTXTS      : VERBATIM,    # This indicates no subcontexts.
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
        iotxt,
        mode,
        store
    ):
# For reading datas.
        self.iotxt = iotxt

# Which storing method must be used ?
        self.store = self.LONG_STORING_MODES.get(store, store)

        if self.store not in self.STORING_MODES:
            raise ValueError("unknown storing mode.")

# Which modes are used ?
        self.mode = Mode(mode)

# Let's build our contexts'rules.
        self.build_ctxts_rules()
        self.build_contents_rules()

# Internal attributs
        self._nbline = 0
        self._line   = None

        self._level              = 0
        self._levels_stack       = []
        self._ctxts_stack        = []
        self._ctxt_sbctxts_stack = []


# ----------------------------- #
# -- INTERNAL CONTEXTS'RULES -- #
# ----------------------------- #

    def build_ctxts_rules(self):
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


# -------------------------------- #
# -- INTERNAL IN-CONTEXTS'RULES -- #
# -------------------------------- #

    def build_contents_rules(self):
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
        for ctxt, configs in self.mode.dicoview.items():
# "keyval" or "multikeyval" modes.
            if configs["mode"] in ["keyval", "multikeyval"]:
                can_use_multikeys = configs["mode"].startswith("multi")

# We must take care of separators with several characters, and we also have to
# escape special characters.
                seps = []

                for onesep in configs["seps"]:
                    if len(onesep) != 1:
                        # onesep = "({0})".format(re.escape(onesep))
                        onesep = "({0})".format(onesep)

                    # else:
                    #     onesep = re.escape(onesep)

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


# "verbatim" mode.
            elif configs["mode"]== "verbatim":
                self.CONTENTS_MATCHERS[ctxt] = ContentInfos(
                    mode       = configs["mode"],
                    id_matcher = id_verbatim
                )


# ------------------- #
# -- BUILD THE AST -- #
# ------------------- #

    def build(self):
        """
This method builds an intermediate AST.
        """
# How do we store things ?
        if self.store == "memory":
            #
            #
            #
            # paser pas stringio !!!! car besoin interface identique !!!
            #
            #

            self.tempfile      = None
            self.view          = []
            self.add           = self._add_in_memory
            self.next_metadata = self._next_meta_in_memory

        else:
            TODO_TEMP

            self.view          = None
            self.tempfile      = Path("???")
            self.add           = self._add_in_temp
            self.next_metadata = self._next_meta_in_temp


# Intermediate AST only for contexts.
        self._verbatim = False

        for line in self.nextline():
            self._line = line
            self.manage_indent()
            self.search_ctxts()

        self.close_ctxt_at_end()

# Final AST with datas in contents.
        self.search_contents()



# -------------------------- #
# -- LOOKING FOR CONTEXTS -- #
# -------------------------- #

    def search_ctxts(self):
        nocontextfound = True

        # print("----> self._ctxts_stack = ", self._ctxts_stack)
        # print("----> self._ctxt_sbctxts_stack = ", self._ctxt_sbctxts_stack)

        for ctxtinfos in self.CTXTS_MATCHERS:
# Not a subcontext ?
            if self._ctxt_sbctxts_stack \
            and (ctxtinfos.openclose, ctxtinfos.kind) \
            not in self._ctxt_sbctxts_stack[-1]:
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

# Not a vsisble new context (be careful of indentation closing)
        if nocontextfound:
            ctxtinfos = self.CTXTINFOS_CONTENT

# We can store the new and eventually close some old contexts.
        self.close_indented_ctxts(ctxtinfos)
        self.store_one_ctxt(ctxtinfos)


    def must_close_indented_ctxt(self):
        if self._levels_stack:
            return self._level <= self._levels_stack[-1]

        return False


    def close_indented_ctxts(self, ctxtinfos):
# Empty lines and autoclosed context with infinite level are the only contexts
# that can't close an indented context.
        if ctxtinfos != self.CTXTINFOS_EMPTYLINE \
        and (
            ctxtinfos.openclose != self.AUTOCLOSE \
            or
            self._level != self.INFINITY
        ):
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

    def last_block_is_container(self):
        if self._matcherstack:
            return self._matcherstack[-1].mode == "container"

        return True

    def search_contents(self):
        self._defaultmatcher = self.CONTENTS_MATCHERS[":default:"]
        self._matcherstack   = []

        for onemeta in self.next_metadata():
            # print(onemeta);continue
# One new block.
            if onemeta['kind'] == "block":
                print("===>     {0}".format(onemeta))

                if onemeta['openclose'] == "open":
# Preceding block must be a container !
                    if not self.last_block_is_container():
                        raise ASTError("lastblock not a container, see line nb.{0}".format(onemeta['line']))

                    self._matcherstack.append(
                        self.CONTENTS_MATCHERS.get(
                            onemeta['groups_found']['name'],
                            self._defaultmatcher
                        )
                    )

                else:
                    self._matcherstack.pop(-1)

# Some content.
            elif onemeta['kind'] == ":content:":
                if not self._matcherstack:
                    raise ASTError("no block before, see line nb.{0}".format(onemeta['line']))

# A good content ?
                if self.match(onemeta['content'], self._matcherstack[-1]):
                    onemeta['content'] = self._groups_found

                print("--->     {0}".format(onemeta))

# Other stuffs no so usefull excpet for cleaning !
            else:
                ...
                print("::->     {0}".format(onemeta))

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
          ????
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


# --------------------------- #
# -- STORING THE METADATAS -- #
# --------------------------- #

    def _add_in_temp(self):
        ...

    def _next_meta_in_temp(self):
        ...


    def _add_in_memory(self, metadatas):
        self.view.append(metadatas)

    def _next_meta_in_memory(self):
        for x in self.view:
            yield x

    def store_one_ctxt(self, ctxtinfos, not_add_groups_alone = True):
        # print('---', self._verbatim, ctxtinfos,sep="\n")

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

        if verbatim:
            verbatim = {
                "kind"   : ":verbatim:",
                "line"   : self._nbline,
                "content": verbatim,
            }

        if ctxtinfos.kind == ":content:":
# We have to keep extra indentations !
            if self._levels_stack[-1] != self.INFINITY \
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



        if ctxtinfos.openclose == self.CLOSE:
            metadatas, verbatim = verbatim, metadatas

        if metadatas:
            self.add(metadatas)

        if verbatim:
            self.add(verbatim)

            if ctxtinfos.openclose == self.OPEN:
                self._verbatim = True

            elif ctxtinfos.openclose == self.CLOSE:
                self._verbatim = False

        if ctxtinfos.openclose == self.AUTOCLOSE:
            new_metadatas = {k: v for k,v in metadatas.items()}
            new_metadatas["openclose"] = self.CLOSE
            self.add(new_metadatas)
