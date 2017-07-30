#! /usr/bin/env python3

"""
prototype::
    date = 2017-07-30


This module contains a class `Clean` for formating a ¨peuf file following some
rules that be customized by the user.
"""

import re

from orpyste.parse.walk import *


# -------------------- #
# -- SAFE CONSTANTS -- #
# -------------------- #

SIZE_TAG = "size"

INDENTLEVEL_TAG = "indentlevel"
LENMAX_TAG      = "lenmax"

SECTION_DECO_CHAR = "="

COMMENT_DECO = {
    OPEN: {
        SINGLELINE: "//",
        MULTILINES: "/*"
    },
    CLOSE: {
        SINGLELINE: "",
        MULTILINES: "*/"
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
        "(^|{spaces}+)(?P<kind>{name}|{abrev})({spaces}+|$)"
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
VAL_LAYOUTS = (
    COLUMNS,
    SPACES,
    SPACES_SECTION,
    SPACES_BLOCK,
    SPACES_COMMENT
) = (
    "columns",
    "spaces",
    "spaces-section",
    "spaces-block",
    "spaces-comment"
)

LONG_VAL_LAYOUTS = {
    "".join(y[0] for y in x.split('-')): x
    for x in VAL_LAYOUTS
}

PATTERNS_VAL_LAYOUTS = {
    re.compile(
        "^((?P<kind>{name}|{abrev})"
        "{spaces}*={spaces}*(?P<size>\d+))({spaces}+|$)"
            .format(
                spaces = "[ \\t]",
                name   = name,
                abrev  = abrev,
            )
    )
    for abrev, name in LONG_VAL_LAYOUTS.items()
}

# ``SPACES_BLOCK`` has by default the same value as ``SPACES``.
#
# ``WRAP_KEYVAL`` and ``WRAP_VERBATIM`` have by default the same value
# as ``WRAP``.
DEFAULT_LAYOUTS = {
    SPACES         : 1,
    SPACES_SECTION : 2,
    SPACES_COMMENT : 0,
    COLUMNS        : 80,
    ALIGN          : False,
    WRAP           : False
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


_METHOD_OPEN_BLOCK, _METHOD_CLOSE_BLOCK     = "open_block", "close_block"
_METHOD_ADD_KEYVAL                          = "add_keyval"
_METHOD_ADD_LINE, _METHOD_ADD_MAGIC_COMMENT = "add_line", "add_magic_comment"


# ----------------------------------- #
# -- DECORATOR(S) FOR THE LAZY MAN -- #
# ----------------------------------- #

def auto_add_extra(meth):
    """
prototype::
    see = Clean

    type = decorator

    arg = method: meth ;
          one method of the class ``Clean``


This decorator helps to add extra stuffs which are the empty decorating lines
and the comments regarding to the contexts.
    """
    def newmeth(self, *args, **kwargs):
        self._methodname = meth.__name__
        self.add_extra()

        return meth(self, *args, **kwargs)

    return newmeth


# -------------- #
# -- CLEANING -- #
# -------------- #

class Clean(WalkInAST):
    """
prototype::
    see = parse.ast.AST , parse.walk.WalkInAST

    arg-attr = str: layout = "" ;
               see the dedicated section below


=================================
One example (without any section)
=================================

The aim of this class is to produce standarized versions of ¨peuf files. Let's
consider the following uggly ¨peuf file.

orpyste::

    /*
     * One example...
     */




    main::

    // Single line comment in the 1st container.


        test::

    /* Comment in a key-val block. */


                aaa = 1

                + 9


                bbbbbbbbb <>
    /* Comment in the value of a key. */
                2
                c                 =       3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and 3 and...


In this file, there are a lot of empty lines and the key-value are strangely
formatted. let's consider the following ¨python script where the variable
``content`` is the string value of the preceding ¨peuf file (as noted later in
this section, you can work directly with a ¨peuf file).

python::
    from orpyste.clean import Clean

    with Clean(
        content = content,
        layout  = "aline wrap columns=50",
        mode    = {
            "container"    : "main",
            "keyval:: = <>": "test"
        }
    ) as datas:
        content_cleaned = "\n".join(line for line in datas.view)


How the preceding code works ?

    1) First we use ``mode``, this variable is fully presented in the
    documentation of ``parse.ast.AST`` (see also the documentation of
    ``orpyste.data.Read``).
    Here we defined blocks named orpyste:``test`` to have key-value like content
    with either orpyste:``=``, or orpyste:``<>`` as a separator. The blocks
    named orpyste:``main`` are containers.

    2) Secondly, and **the most important here**, we use ``layout = "aline
    wrap"`` so as to align the keys and their values regarding their separators,
    and also to wrap long values like the last one with ``3 and 3 and...``.
    As you can see several options can be used if they are separated by at least
    one space.

    3) When you call the context manager, indeed the class uses, more or less,
    the methods ``build`` when the context is opened, and ``remove_extras`` to
    close the context (see the class ``parse.walk.WalkInAST``).


The string value of ``content_cleaned`` is finally the following one which looks
a little prettier.

orpyste::
    /*
     * One example...
     */

    main::
    // Single line comment in the 1st container.

        test::
    /* Comment in a key-val block. */

            aaa        = 1 + 9

    /* Comment in the value of a key. */

            bbbbbbbbb <> 2
            c          = 3 and 3 and 3 and 3 and 3 and
                         3 and 3 and 3 and 3 and 3 and
                         3 and 3 and 3 and 3 and 3 and
                         3 and 3 and 3 and 3 and 3 and
                         3 and 3 and 3 and 3 and 3 and
                         3 and 3 and 3 and...


info::
    Here we have worked with a string, but you can work with a file using the
    class ``pathlib.Path``. The syntax remains the same.


info::
    For verbatim block contents, you can ask to keep final empty lines by adding
    orpyste::``////`` at the end of the content.


==================
Setting the layout
==================

Here are all the options of the argument ``layout``.

    1) ``"align"`` or ``"a"`` asks to align the separators in a block made of
    keys and values. By default, this option is not actived.

    2) ``"columns"`` or ``"c"`` gives the number of columns of the file if the
    wrap mode is used (see below). By default, the class uses "columns=80".

    3) ``"spaces"`` or ``"s"`` allows to define the number of empty lines after
    blocks and comments. You can use more precisely ``"spaces-comment"`` or
    ``"sc"`` only for spacing after comments, and ``"spaces-block"`` or ``"sb"``
    only for spacing after blocks.
    By default, ``"spaces-section = 2"``, ``"spaces-block = 1"`` and
    ``"spaces-comment = 0"``.

    4) ``"wrap"`` or ``"w"`` makes the cleaned content hard wrapped. There are
    also ``"wrap-verbatim"`` or ``"wv"``, and ``"wrap-keyval"`` or ``"wk"`` only
    to wrap verbatim and key-value contents respectivly. By default, the content
    is not wrapped.


info::
    Several options can be used simply if they are separated by at least one
    space.


info::
    All the default setting are stored in the class attribut ``DEFAULT_LAYOUTS``
    whose default definition is the following one.

    python::
        DEFAULT_LAYOUTS = {
            SPACES         : 1,
            SPACES_SECTION : 2,
            SPACES_COMMENT : 0,
            COLUMNS        : 80,
            ALIGN          : False,
            WRAP           : False
        }

    You can use this class attribut so as to alwways use the same setting
    instead of using the argument ``layout``.
    """

    def __init__(
        self,
        content,
        mode,
        encoding = "utf-8",
        layout   = ""
    ):
        super().__init__(
            content  = content,
            mode     = mode,
            encoding = encoding
        )

        self.layout = layout

# -- SPECIAL SETTER FOR THE LAYOUT -- #

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout  = DEFAULT_LAYOUTS
        settingsfound = set()

# We must search first the single layout settings.
        for regex in PATTERNS_BOOL_LAYOUTS:
            search = regex.search(value)

            if search:
                start, end = search.span()
                kind       = search.groupdict()[KIND_TAG]
                kind       = LONG_BOOL_LAYOUTS.get(kind, kind)

                self._layout[kind] = True
                settingsfound.add(kind)

# We have to remove the winning matching.
                value = "{0} {1}".format(value[:start], value[end:])

# Now we can look for layout settings with a numerical value.
        value = value.strip()

        while value:
            nomatchfound = True

            for regex in PATTERNS_VAL_LAYOUTS:
                search = regex.search(value)

                if search:
                    nomatchfound = False
                    start, end   = search.span()
                    kind         = search.groupdict()[KIND_TAG]
                    kind         = LONG_VAL_LAYOUTS.get(kind, kind)
                    size         = search.groupdict()[SIZE_TAG]

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
        for onelayout in ALL_LAYOUTS - settingsfound:
            if onelayout in PARENT_LAYOUTS:
                parent = PARENT_LAYOUTS[onelayout]

                if parent in settingsfound:
                    self._layout[onelayout] = self._layout[parent]

# Internal attributs so as to ease the coding.
        for key, value in self._layout.items():
            setattr(
                self,
                "_{0}".format(key.replace("-", "_")),
                value
            )

# -- ADDITIONAL METHODS -- #

    def isnotfirstline(self):
        if not self._isnotfirstline:
            self._isnotfirstline = True
            return False

        return True

    def add_indentation(self, text, indentlevel, addempty = False):
        """
prototype::
    arg = str: text
    arg = int: indentlevel

    return = str ;
             the text with leading ``indentlevel`` tabulations ``ONETAB``
             added
        """
        if text or addempty:
            text = "{0}{1}".format(ONETAB*indentlevel, text)

        return text

    def add_empty(self):
        """
Sometimes, we need to add an empty meaningless content. This method does this.
        """
        self.walk_view.write((None, ""))

    def wrap(self, text):
        """
prototype::
    arg = str: text

    return = str ;
             the text wrapped regarding the value of ``self._columns``
        """
        if len(text) > self._columns and (
            (self._mode == KEYVAL and self._wrap_keyval)
            or
            (self._mode == VERBATIM and self._wrap_verbatim)
        ):
# "key-value" mode
            if self._mode == KEYVAL:
                extraspaces = self.add_indentation(
                    text        = self._kv_extra_spaces,
                    indentlevel =self.indentlevel
                )

                textsplitted \
                = text[len(self._lastkeysep_indented):].split()

                newtext = [self._lastkeysep_indented]

# VERBATIM mode
            else:
                extraspaces = self.add_indentation(
                    text        = "",
                    indentlevel = self.indentlevel,
                    addempty    = True
                )[:-1]

                newtext, *textsplitted = text.split()

                newtext = [
                    self.add_indentation(
                        text        = newtext,
                        indentlevel = self.indentlevel
                    )
                ]


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

    def add_extra(self):
# Comments to be added ?
        if self._last_comments == []:
            return

# Verbatim is verbatim ! Comments stay where they was !
        if self.last_mode == VERBATIM:
            while(self._last_comments):
                self.add_next_comment(mustaddspaces = False)

        else:
# Comments before an opening block
            if self._methodname == _METHOD_OPEN_BLOCK:
                if self.last_mode.endswith(KEYVAL):
                    self._isnotfirstkeyval = False

                if not self.isnotfirstline():
                    self._iscommentendblock = True

                while(self._last_comments):
                    self.add_next_comment()

# Comments at the end of an opening block (this is our
# choice !)
            elif self._methodname == _METHOD_CLOSE_BLOCK:
                self._iscommentendblock = True

                self.add_spaces(SPACES_BLOCK)

                while(self._last_comments):
                    self.add_next_comment()

# Others comments
            else:
                inside_keyval_block = bool(
                    self.modes_stack
                    and self.modes_stack[-1].endswith(KEYVAL)
                    and 0 < self.kv_nbline
                )

                if self._isnotfirstkeyval:
                    self.add_spaces(SPACES_COMMENT)

                else:
                    self._isnotfirstkeyval = True

                while(self._last_comments):
                    if inside_keyval_block:
                        if self.kv_nbline < self._last_comments[0][NBLINE_TAG]:
                            break

                    self.add_next_comment()

    def add_next_comment(self, mustaddspaces = True):
        onecomment = self._last_comments.pop(0)

        kind = onecomment[KIND_TAG]

        if kind.startswith(MULTILINES):
            kind = MULTILINES

        self.walk_view.write((
            None,
            "{0}{1}{2}".format(
                COMMENT_DECO[OPEN][kind],
                "\n".join(onecomment[CONTENT_TAG]),
                COMMENT_DECO[CLOSE][kind]
            )
        ))

        if mustaddspaces:
            self.add_spaces(SPACES_COMMENT)

    def add_spaces(self, kind):
        for _ in range(self._layout[kind]):
            self.walk_view.write((None, ""))

# -- START AND END OF FILE -- #

    def start(self):
# We have to take care of some extra stuffs !
        self._infos             = {}
        self._last_comments     = []
        self._isnotfirstline    = False
        self._startingsection   = False
        self._isnotfirstkeyval  = False
        self._iscommentendblock = False

    @auto_add_extra
    def end(self):
# The final job can be done !
        self.view = IOView("list")
        text = ""

        with self.view:
# We have to follow the user's layout !
            for (self._mode, extra_text) in self.walk_view:
                if self._mode == KEYVAL:
                    key   = extra_text[KEY_TAG]
                    sep   = extra_text[SEP_TAG]
                    value = extra_text[VAL_TAG]

                    if self._layout[ALIGN]:
                        keyformat = "{" + ":<{0}".format(lenkey) + "}"
                        key       = keyformat.format(key)

                        sepformat = "{" + ":>{0}".format(lensep) + "}"
                        sep       = sepformat.format(sep)


                    keysep = "{0} {1}".format(key, sep)

                    self._kv_extra_spaces = " "*len(keysep)

                    self._lastkeysep_indented = self.add_indentation(
                        text        = keysep,
                        indentlevel = self.indentlevel
                    )

                    text = "{lastkeysep} {value}".format(
                        lastkeysep = self._lastkeysep_indented,
                        value      = value
                    )

                else:
                    text = extra_text

                    if self._mode == VERBATIM:
                        text = self.add_indentation(
                            text        = text,
                            indentlevel = self.indentlevel
                        )

                    elif self._mode in self._infos:
                        if self._layout[ALIGN] \
                        and self._infos[self._mode][MODE_TAG] == KEYVAL:
                            lenkey, lensep = self._infos[self._mode][LENMAX_TAG]

                        self.indentlevel \
                        = self._infos[self._mode][INDENTLEVEL_TAG]

                text = self.wrap(text)

                self.view.write(text)

# An empty line at the end !
        if text:
            self.view.write("")

# -- FOR SECTIONS -- #

    @auto_add_extra
    def section_title(self, title):
        if self.isnotfirstline():
            self.add_spaces(SPACES_SECTION)

        deco = SECTION_DECO_CHAR * len(title)

        self.walk_view.write((SECTION_TAG, deco))
        self.walk_view.write((SECTION_TAG, title))
        self.walk_view.write((SECTION_TAG, deco))

        self._startingsection = True

# -- FOR COMMENTS -- #

    def open_comment(self, kind):
        self._last_comments.append({
            NBLINE_TAG : self.metadata[NBLINE_TAG],
            KIND_TAG   : kind,
            CONTENT_TAG: []
        })

    def content_in_comment(self, line):
        self._last_comments[-1][CONTENT_TAG].append(line)

# -- FOR BLOCKS -- #

    @auto_add_extra
    def open_block(self, name):
        if self.modes_stack[-1] != CONTAINER:
            self._last_tag = "{0}@{1}".format(
                self.metadata[NBLINE_TAG],
                self.metadata[KIND_TAG]
            )

            self._infos[self._last_tag] = {
                INDENTLEVEL_TAG: self.indentlevel + 1,
                MODE_TAG       : self.modes_stack[-1]
            }

        else:
            self._last_tag = self.metadata[KIND_TAG]

        if self.modes_stack[-1].startswith(KEYVAL):
            if self._layout[ALIGN]:
                self._infos[self._last_tag][LENMAX_TAG] = (0, 0)

        if not self._iscommentendblock \
        and self.isnotfirstline():
            self.add_spaces(SPACES_BLOCK)

        self.walk_view.write(
            (
                self._last_tag,
                "{0}::".format(
                    self.add_indentation(
                        text        = name,
                        indentlevel = self.indentlevel
                    )
                )
            )
        )

        self._iscommentendblock = False
        self._startingsection   = False

        if self.last_mode == CONTAINER:
            self._isnotfirstline = False

    @auto_add_extra
    def close_block(self, name):
        ...

# -- (MULTI)KEYVAL -- #

    @auto_add_extra
    def add_keyval(self, keyval):
        self.walk_view.write((KEYVAL, keyval))

        if self._layout[ALIGN]:
            keylen, seplen = self._infos[self._last_tag][LENMAX_TAG]

            keylen = max(len(keyval[KEY_TAG]), keylen)
            seplen = max(len(keyval[SEP_TAG]), seplen)

            self._infos[self._last_tag][LENMAX_TAG] = (keylen, seplen)

# -- VERBATIM -- #

    @auto_add_extra
    def add_magic_comment(self):
        self.walk_view.write((MAGIC_COMMENT, "////"))

    @auto_add_extra
    def add_line(self, line):
        self.walk_view.write((VERBATIM, line))
