#! /usr/bin/env python3

"""
prototype::
    date = 2015-11-???


ALIORERE AVEC UN PEU ESPACE !!!!!!!

This module contains a class `Clean` so as to format a ¨peuf file following some
rules that be customized by the user.
"""

import re

from orpyste.parse.walk import IOView, WalkInAST


# ----------------------------------- #
# -- DECORATOR(S) FOR THE LAZY MAN -- #
# ----------------------------------- #

def closecomments(meth):
    """
property::
    see = Clean

    type = decorator

    arg = func: meth ;
          one method of the class ``Clean``


This decorator helps to close easily comments in different contexts.
    """
    def newmeth(self, *args, **kwargs):
        self.close_comments()

        return meth(self, *args, **kwargs)

    return newmeth


# -------------- #
# -- CLEANING -- #
# -------------- #

class Clean(WalkInAST):
    """
prototype::
    see = parse.ast.AST , parse.walk.WalkInAST

    arg-attr = pathlib.Path, str: content ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str, dict: mode ;
               see the documentation of ``parse.ast.AST``
    arg-attr = str: layout = "" ;
               see the dedicated section below


===========
One example
===========

?????





Here is an example using the class ``Clean``. We use the argument ``mode`` to
indicate that blocks named orpyste::``test`` are for key-value contents,
whereas other blocks are just containers. We also use ``layout = "aline wrap"``
so as to align the keys and their values regarding their separators, and also to
wrap long values like the last one with ``3 and 3 and...``. As you can see
several options can be used if they are separated by at least one



.

pyterm::
????


Here we have worked with in-memory objects. The content being stored in a
strong, the class used internaly list of strings and returns a string. Indeed
you can work woth files using the class ``pathlib.Path``. Here is an example
of use.

pyterm::
????


======================
Settings of the layout
======================

We give above all the layout options. You must know that several options can be
used simply if they are separated by at least one space.

    1) "align" or "a"
        ---> gérer problème clé très longue

    1) "columns" or "c"
        ---> gérer problème clé très longue

    1) "spaces" or "s"
        ---> espace après
    "spaces-comment" or "sc"
        --->
    "spaces-block" or "sb"
        --->

    1) "wrap" or "w"    Z!! on doit garder les espaces multiples !!!!
        ---> retour à la ligne pour tout !
    "wrap-verbatim" or "wv"
        ---> retour à la ligne mais pas de collage
    "wrap-keyval" or "wk"
        --->  retour à la ligne avec collage et on tient compte du spératur si align


    nbre espaces avant-après
        ---> ????
    """

    COMMENT_DECO = {
        "open": {
            "singleline": "//",
            "multilines": "/*"
        },
        "close": {
            "singleline": "",
            "multilines": "*/"
        },
    }

    BOOL_LAYOUTS \
    = ALIGN, WRAP, WRAP_VERBATIM, WRAP_KEYVAL \
    = "align", "wrap", "wrap-verbatim", "wrap-keyval"

    LONG_BOOL_LAYOUTS = {
        "".join(
            y[0] for y in x.split('-')
        ): x
        for x in BOOL_LAYOUTS
    }

    PATTERNS_BOOL_LAYOUTS = {
        re.compile(
            "(^|{spaces}+)(?P<kind>{name}|{abrev})({spaces}+|$)" \
                .format(
                    spaces = "[ \\t]",
                    name   = name,
                    abrev  = abrev,
                )
        )
        for abrev, name in LONG_BOOL_LAYOUTS.items()
    }

# << WARNING ! >> Keep the following lines in case of future more advanced
# features !
    VAL_LAYOUTS \
    = COLUMNS, SPACES, SPACES_BLOCK, SPACES_COMMENT \
    = "columns", "spaces", "spaces-block", "spaces-comment"

    LONG_VAL_LAYOUTS = {
        "".join(y[0] for y in x.split('-')): x
        for x in VAL_LAYOUTS
    }

    PATTERNS_VAL_LAYOUTS = {
        re.compile(
            "^((?P<kind>{name}|{abrev})"
            "{spaces}*={spaces}*(?P<size>\d+))({spaces}+|$)" \
                .format(
                    spaces = "[ \\t]",
                    name   = name,
                    abrev  = abrev,
                )
        )
        for abrev, name in LONG_VAL_LAYOUTS.items()
    }

    DEFAULT_LAYOUTS = {
        SPACES        : 2,
        SPACES_COMMENT: 1,
        COLUMNS       : 80,
        ALIGN         : False,
# ``WRAP_KEYVAL`` and ``WRAP_VERBATIM`` have by default the same value
# than ``WRAP``.
        WRAP: False
    }

    ALL_LAYOUTS = set(BOOL_LAYOUTS) | set(VAL_LAYOUTS)

    PARENT_LAYOUTS = {}

    for x in ALL_LAYOUTS:
        if "-" in x:
            parent, _ = x.split('-')

            PARENT_LAYOUTS[x] = parent

            if x not in DEFAULT_LAYOUTS:
                DEFAULT_LAYOUTS[x] = DEFAULT_LAYOUTS[parent]

    ONETAB = " "*4


    def __init__(
        self,
        content,
        mode,
        layout = ""
    ):
        super().__init__(content = content, mode = mode)

        self.layout = layout
        self.onetab = self.ONETAB


# ----------------------------------- #
# -- SPECIAL SETTER FOR THE LAYOUT -- #
# ----------------------------------- #

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout  = self.DEFAULT_LAYOUTS
        settingsfound = set()

# We must search first the single layout settings.
        for regex in self.PATTERNS_BOOL_LAYOUTS:
            search = regex.search(value)

            if search:
                start, end = search.span()
                kind       = search.groupdict()["kind"]
                kind       = self.LONG_BOOL_LAYOUTS.get(kind, kind)

                self._layout[kind] = True
                settingsfound.add(kind)

# We have to remove the winning matching.
                value = "{0} {1}".format(value[:start], value[end:])

# Now we can look for layout settings with a numerical value.
        value = value.strip()

        while value:
            nomatchfound = True

            for regex in self.PATTERNS_VAL_LAYOUTS:
                search = regex.search(value)

                if search:
                    nomatchfound = False
                    start, end   = search.span()
                    kind         = search.groupdict()["kind"]
                    kind         = self.LONG_VAL_LAYOUTS.get(kind, kind)
                    size         = search.groupdict()["size"]

                    self._layout[kind] = int(size)
                    settingsfound.add(kind)

# We have to remove the winning matching.
                    value = "{0} {1}".format(value[:start], value[end:])
                    value = value.strip()

                if not value:
                    break

# Nothing must remain.
            if nomatchfound:
                raise ValueError(
                    "unknown layout setting. See << {0} >>.".format(value)
                )

# Parent settings
        for onelayout in self.ALL_LAYOUTS - settingsfound:
            if onelayout in self.PARENT_LAYOUTS:
                parent = self.PARENT_LAYOUTS[onelayout]

                if parent in settingsfound:
                    self._layout[onelayout] = self._layout[parent]

# Internal attributs so as to ease the coding.
        for key, value in self._layout.items():
            setattr(
                self,
                "_{0}".format(key.replace("-", "_")),
                value
            )


# ------------------------ #
# -- ADDITIONAL METHODS -- #
# ------------------------ #

    def add_indentation(self, text, indentlevel):
        """
prototype::
    ???
        """
        return "{0}{1}".format(self.onetab*indentlevel, text)


    def add_empty(self):
        """
prototype::
    ???
        """
        if self._datasfound:
            self.walk_view.write((None, "??"))


    def wrap(self, text):
        """
prototype::
    ???
        """
        if len(text) > self._columns and (
            (
                self._mode == "keyval" and self._wrap_keyval
            ) or (
                self._mode == "verbatim" and self._wrap_verbatim
            )
        ):
# "key-value" mode
            if self._mode == "keyval":
                extraspaces = self.add_indentation(
                    self._kv_extra_spaces,
                    self.indentlevel
                )

                textsplitted \
                = text[len(self._lastkeysep_indented):].split()

                newtext = [self._lastkeysep_indented]

# "verbatim" mode
            else:
                extraspaces = self.add_indentation("", self.indentlevel)[:-1]

                newtext, *textsplitted = text.split()

                newtext = [self.add_indentation(newtext, self.indentlevel)]


            for word in textsplitted:
                if len(word) + len(newtext[-1]) >= self._columns:
                    newtext.append("{0} {1}".format(
                        extraspaces,
                        word
                    ))

                else:
                    newtext[-1] = "{0} {1}".format(
                        newtext[-1],
                        word
                    )

            return "\n".join(newtext)

# Nothing to do !
        return text


    def close_comments(self):
        """
prototype::
    ???
        """
        while(self._comment):
            if (
                self.modes_stack
                and self.modes_stack[-1].endswith("keyval")
                and not self._isblockempty
                and self.kv_nbline < self._comment[0]['line']
            ):
                break

            kind = self._comment[0]['kind']

            if kind.startswith('multilines'):
                kind = 'multilines'

            if not self._isblockempty:
                self.walk_view.write((None, ""))

            self.walk_view.write((
                None,
                "{0}{1}{2}".format(
                    self.COMMENT_DECO['open'][kind],
                    "\n".join(self._comment.pop(0)['content']),
                    self.COMMENT_DECO['close'][kind]
                )
            ))

            self.add_spaces(self.SPACES_COMMENT)


    def add_spaces(self, kind):
        for _ in range(self._layout[kind]):
            self.walk_view.write(("verbatim", ""))


# --------------------------- #
# -- START AND END OF FILE -- #
# --------------------------- #

    def start(self):
# We have to take care of some extra stuffs !
        self._infos              = {}
        self._datasfound         = False
        self._isblockempty       = True
        self._block_closed_alone = True
        self._comment            = []


    def end(self):
# The final job can be done !
        self.view = IOView(self.walk_view.mode)

        with self.view:
# We have to follow the user's layout !
            for (self._mode, extra_text) in self.walk_view:
                if self._mode == "keyval":
                    key   = extra_text["key"]
                    sep   = extra_text["sep"]
                    value = extra_text["value"]

                    if self._layout[self.ALIGN]:
                        keyformat = "{" + ":<{0}".format(lenkey) + "}"
                        key       = keyformat.format(key)

                        sepformat = "{" + ":>{0}".format(lensep) + "}"
                        sep       = sepformat.format(sep)


                    keysep = "{0} {1}".format(key, sep)

                    self._kv_extra_spaces = " "*len(keysep)

                    self._lastkeysep_indented = self.add_indentation(
                        keysep,
                        self.indentlevel
                    )

                    text = "{lastkeysep} {value}".format(
                        lastkeysep = self._lastkeysep_indented,
                        value      = value
                    )

                else:
                    text = extra_text

                    if self._mode == "verbatim":
                        text = self.add_indentation(text, self.indentlevel)

                    elif self._mode in self._infos:
                        if self._layout[self.ALIGN] \
                        and self._infos[self._mode]["mode"] == "keyval":
                            lenkey, lensep = self._infos[self._mode]["lenmax"]

                        self.indentlevel = self._infos[self._mode]["indentlevel"]

                text = self.wrap(text)

                self.view.write(text)


# ------------------ #
# -- FOR COMMENTS -- #
# ------------------ #

    def open_comment(self, kind):
        self._comment.append({
            "line"   : self.metadata["line"],
            "kind"   : kind,
            "content": []
        })


    def content_in_comment(self, line):
        self._comment[-1]["content"].append(line)


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    @closecomments
    def open_block(self, name):
        self._datasfound   = True
        self._isblockempty = True

        self._block_closed_alone = True

        if self.modes_stack[-1] != "container":
            self._last_tag = "{0}@{1}".format(
                self.metadata["line"],
                self.metadata["kind"]
            )

            self._infos[self._last_tag] = {
                "indentlevel": self.indentlevel + 1,
                "mode"       : self.modes_stack[-1]
            }

        else:
            self._last_tag = self.metadata["kind"]

        if self.modes_stack[-1].startswith("keyval"):
            if self._layout[self.ALIGN]:
                self._infos[self._last_tag]["lenmax"] = (0, 0)

        self.walk_view.write(
            (
                self._last_tag,
                "{0}::".format(
                    self.add_indentation(name, self.indentlevel)
                )
            )
        )

    def close_block(self, name):
        if self._block_closed_alone:
            self.add_spaces(self.SPACES_BLOCK)
            self._block_closed_alone = False


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    @closecomments
    def add_keyval(self, keyval):
        if self._isblockempty:
            self._isblockempty = False

        self.walk_view.write(("keyval", keyval))

        if self._layout[self.ALIGN]:
            keylen, seplen = self._infos[self._last_tag]["lenmax"]

            keylen = max(len(keyval["key"]), keylen)
            seplen = max(len(keyval["sep"]), seplen)

            self._infos[self._last_tag]["lenmax"] = (keylen, seplen)


# -------------- #
# -- VERBATIM -- #
# -------------- #

    @closecomments
    def add_magic_comment(self):
        self.walk_view.write(("magic-comment", "////"))


    @closecomments
    def add_line(self, line):
        self.walk_view.write(("verbatim", line))
