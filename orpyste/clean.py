#! /usr/bin/env python3

"""
prototype::
    date = 2015-07-03


This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.


système un peu fin
    --> l-gne vide qui se suive réuni sausf si ....
    --> gestion séparé du nettoyage hors commentaire ou dans commentaire
    --> pour le reste on garde un truc normatif malgré tout
"""

import re
from orpyste.parse import ast, walk


# -------------------------------- #
# -- DECORATOR FOR THE LAZY MAN -- #
# -------------------------------- #

def closecomments(meth):
    """
property::
    type = decorator

    arg = func: meth ;
          ????
    """
    def newmeth(inst, *args, **kwargs):
        while(inst._comment):
            if (
                inst.modes_stack[-1].endswith("keyval") \
                and
                not inst._blockisempty
                and
                inst.kv_nbline < inst._comment[0]['line']
            ):
                break

            kind = inst._comment[0]['kind']

            if kind.startswith('multilines'):
                kind = 'multilines'

            inst.remove_unuseful_empty(-1)

            if not inst._blockisempty:
                inst._modes_extra_texts.append((None, ""))

            inst._modes_extra_texts.append((
                None,
                "{0}{1}{2}".format(
                    inst.COMMENT_DECO['open'][kind],
                    "\n".join(inst._comment.pop(0)['content']),
                    inst.COMMENT_DECO['close'][kind]
                )
            ))

            for i in range(inst._space_comment):
                inst._modes_extra_texts.append((None, ''))


        return meth(inst, *args, **kwargs)

    return newmeth


# -------------- #
# -- CLEANING -- #
# -------------- #

class Clean(walk.WalkInAST):
    """


un premier passage pour récupérer méta donné sur clé valeurs ( f mef via align)
après end se charge de finir e travail


gestion du lode wrap

gestion de l'alignement face aux symbole key-val
    ---> phase 1 avec tout sur une ligne, on en profite pour mémoriser les choses utiles (on peut ainsi bosser sur de gros dossiers même si cela complique un peu les choses)
    ---> gérer cas d'un clé hyper longue ! dans ce cas  on fait un retour à la ligne avec une simple tabulation

personnalisation
    ---> espaces pour fin de commentaire et de bloc et autre
    ---> align pour keyval
    ---> wrapp mode(pour keyval et verbatim à part)

    layout = "space=4 space-comment=4 space-block=1 align wrap wrap-verbatim wrap-keyval"


    "align"
        ---> gérer problème clé très longue

    "wrap"    Z!! on doit garder les espaces multiples !!!!
        ---> retour à la ligne pour tout !
    "wrap-verbatim"
        ---> retour à la ligne mais pas de collage
    "wrap-keyval"
        --->  retour à la ligne avec collage et on tient compte du spératur si align

    "space = 4"
        ---> 4 espaces après commentaires et bloc
    "space-comment = 4"
        ---> 4 espaces après commentaires
    "space-block = 4"
        ---> 4 espaces après bloc

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

    ALIGN, WRAP, WRAP_VERBATIM, WRAP_KEYVAL \
    = "align", "wrap", "wrap-verbatim", "wrap-keyval"

    BOOL_LAYOUTS = [ALIGN, WRAP, WRAP_VERBATIM, WRAP_KEYVAL]

    LONG_BOOL_LAYOUTS = {
        "".join(
            y[0] for y in x.split('-')
        ): x
        for x in BOOL_LAYOUTS
    }

    PATERNS_BOOL_LAYOUTS = {
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

    COLUMNS, SPACE, SPACE_COMMENT, SPACE_BLOCK \
    = "columns", "space", "space-comment", "space-block"

    VAL_LAYOUTS = [COLUMNS, SPACE, SPACE_COMMENT, SPACE_BLOCK]

    LONG_VAL_LAYOUTS = {
        "".join(
            y[0] for y in x.split('-')
        ): x
        for x in VAL_LAYOUTS
    }

    PATERNS_VAL_LAYOUTS = {
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
        COLUMNS: 80,
        ALIGN  : False,
# ``WRAP_KEYVAL`` and ``WRAP_VERBATIM`` have by default the same value
# than ``WRAP``.
        WRAP : False,
# ``SPACE_BLOCK`` and ``SPACE_COMMENT`` have by default the same value
# than ``SPACE``.
        SPACE : 1
    }

    ALL_LAYOUTS = set(BOOL_LAYOUTS + VAL_LAYOUTS)

    PARENT_LAYOUTS = {}

    for x in ALL_LAYOUTS:
        if "-" in x:
            parent, _ = x.split('-')
            PARENT_LAYOUTS[x] = parent
            DEFAULT_LAYOUTS[x] = DEFAULT_LAYOUTS[parent]

    def __init__(
        self,
        content,
        mode,
        layout = ""
    ):
# Public attributs
        self.content = content
        self.mode    = mode
        self.layout  = layout


# -------------------- #
# -- SPECIAL SETTER -- #
# -------------------- #

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout  = self.DEFAULT_LAYOUTS
        settingsfound = set([])

# We must search first the single layout settings.
        for regex in self.PATERNS_BOOL_LAYOUTS:
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

            for regex in self.PATERNS_VAL_LAYOUTS:
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
        self._align         = self._layout[self.ALIGN]
        self._columns       = self._layout[self.COLUMNS]
        self._wrap_verbatim = self._layout[self.WRAP_VERBATIM]
        self._wrap_keyval   = self._layout[self.WRAP_KEYVAL]
        self._space_block   = self._layout[self.SPACE_BLOCK]
        self._space_comment = self._layout[self.SPACE_COMMENT]


# ------------------------ #
# -- ADDITIONAL METHODS -- #
# ------------------------ #

    def add_indentation(self, text, indentlevel):
        return "{0}{1}".format(" "*4*indentlevel, text)


    def remove_unuseful_empty(self, i):
        while(
            self._modes_extra_texts
            and
            self._modes_extra_texts[i][1] == ''
        ):
            self._modes_extra_texts.pop(i)


    def wrap(self, text):
# TODO factorisation !!!!
        if len(text) > self._columns and (
            (
                self._mode == "keyval" and self._wrap_keyval
            ) or (
                self._mode == "verbatim" and self._wrap_verbatim
            )
        ):
            if self._mode == "keyval":
                extraspaces = self.add_indentation(
                    self._kv_extra_spaces,
                    self.indentlevel
                )

                textsplitted \
                = text[len(self._lastkeysep_indented):].split()

                newtext = [self._lastkeysep_indented]

            else:
                extraspaces = self.add_indentation("", self.indentlevel)[:-1]

                newtext, *textsplitted = text.split()
                newtext      = [
                    self.add_indentation(newtext, self.indentlevel)
                ]


            for word in textsplitted:
                newtext[-1] = "{0} {1}".format(
                    newtext[-1],
                    word
                )

                if len(newtext[-1]) > self._columns:
                    newtext.append(extraspaces)

            if newtext[-1] == extraspaces:
                newtext.pop(-1)

            return "\n".join(newtext)

# Nothing to do !
        return text


# --------------------------- #
# -- START AND END OF FILE -- #
# --------------------------- #

    def start(self):
        self._comment           = []
        self._modes_extra_texts = []
        self._infos             = {}


    def end(self):
# We clean empty lines at the begining and the end of the content.
        for i in [0, -1]:
            self.remove_unuseful_empty(i)

# User's layout !
        for (self._mode, extra_text) in self._modes_extra_texts:
            # print((self._mode, extra_text));continue
            if self._mode == "keyval":
                key   = extra_text["key"]
                sep   = extra_text["sep"]
                value = extra_text["value"]

                if self._layout["align"]:
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
                    if self._layout["align"] \
                    and self._infos[self._mode]["mode"] == "keyval":
                        lenkey, lensep = self._infos[self._mode]["lenmax"]

                    self.indentlevel \
                    = self._infos[self._mode]["indentlevel"]


            text = self.wrap(text)
            print(text)





# ------------------ #
# -- FOR COMMENTS -- #
# ------------------ #

    def open_comment(self):
        self._comment.append({
            "line"   : self.metadata["line"],
            "kind"   : self.metadata["kind"][8:],
            "content": []
        })

    def content_in_comment(self, line):
        self._comment[-1]["content"].append(line)


# ---------------- #
# -- FOR BLOCKS -- #
# ---------------- #

    @closecomments
    def open_block(self, name):
        # print("====\nopen ??", self.metadata["line"], name)

        self._blockisempty = True

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
            if self._layout["align"]:
                self._infos[self._last_tag]["lenmax"] = (0, 0)

        self._modes_extra_texts.append(
            (
                self._last_tag,
                "{0}::".format(
                    self.add_indentation(name, self.indentlevel)
                )
            )
        )


    @closecomments
    def close_block(self):
        # print("close ??", self.indentlevel)
        self.remove_unuseful_empty(-1)

        for i in range(self._space_block):
            self._modes_extra_texts.append((None, ''))


# ------------------- #
# -- (MULTI)KEYVAL -- #
# ------------------- #

    @closecomments
    def addkeyval(self, keyval):
        if self._blockisempty == True:
            self._blockisempty = False

        self._modes_extra_texts.append(("keyval", keyval))

        if self._layout["align"]:
            keylen, seplen = self._infos[self._last_tag]["lenmax"]

            keylen = max(len(keyval["key"]), keylen)
            seplen = max(len(keyval["sep"]), seplen)

            self._infos[self._last_tag]["lenmax"] = (keylen, seplen)


# -------------- #
# -- VERBATIM -- #
# -------------- #

    @closecomments
    def addline(self, line):
        if line:
            if self._blockisempty == True:
                self._blockisempty = False

            self._modes_extra_texts.append(("verbatim", line))

        elif not (
            self._blockisempty
            or
            self.modes_stack[-1].endswith('keyval')
        ):
            self._modes_extra_texts.append((None, ''))
