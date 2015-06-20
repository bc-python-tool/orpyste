#! /usr/bin/env python3

"""
prototype::
    date = 2015-????


This module ????

allows to read efficient to type and simple structured string datas
contained in files using the ``peuf`` specifications.
"""

from orpyste.parse import ast, pyit


# ------------- #
# -- READING -- #
# ------------- #

class Read():
    """
prototype::
    see = parse

    arg = file, io.StringIO: iotxt ;
          ???
          either  f = open("myfile.txt", "r", encoding="utf-8")
          In-memory text streams are also available as StringIO objects:
          or
          f = io.StringIO("some initial text data")

    arg = passer par une classe via un mode simple de config
        : config ;
        str: mode = "keyval::=" with {keyval} in self.IN_CTXTS
                                                or in self.LONG_IN_CTXTS ;

          si string c'est que pour des blocs de niveau 1 tus du même type


          keyval        onekey=...
          multikeyval   multikey=...
          line          line by line content
          verbatim      single verbaitm string !!!!

          = ou plusieurs opérateurs sans esapce commme dans
          multikeyval:: = < >

          espace de début pour lisibiliré uniquement


          dict comme avant toujours possible car pratqiue au jour le jour

          config via classe dédié pour cas complexe ou typage des données si besoin`

          Z !!!! Par contre on doit passer par classe dédiée qu el'on met en fait ici



    arg = str: store = "memory" in self.STORING_MODES
                              or in self.LONG_STORING_MODES ;



???
    """
    AST  = ast.AST
    PYIT = pyit.AST2PY

    def __init__(
        self,
        iotxt,
        mode  = "keyval::=",
        store = "memory"
    ):
# Public attributs
        self.iotxt = iotxt
        self.mode  = mode
        self.store = store


# --------------------- #
# -- BUILD THE DATAS -- #
# --------------------- #

    def build(self):
# We build the AST view.
        _AST = self.AST(
            iotxt = self.iotxt,
            mode  = self.mode,
            store = self.store
        )

        _AST.build()






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
