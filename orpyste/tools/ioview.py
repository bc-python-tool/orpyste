#! /usr/bin/env python3

"""
prototype::
    date = 2016-07-24


This module gives an easy way to work either with a pickle file or with a list
so as to store and read datas.
"""

import pickle


# -------------------- #
# -- SAFE CONSTANTS -- #
# -------------------- #

IO_TYPES = LIST, PICKLE = "list", "pickle"

LONG_IO_TYPES = {x[0]: x for x in IO_TYPES}


# --------------- #
# -- THE CLASS -- #
# --------------- #

class IOView():
    """
prototype::
    arg-attr = str: mode in IO_TYPES
                      or in LONG_IO_TYPES ;
               if ``mode = "list"`` then you will work with a list, and if
               ``mode = "pickle"`` then you will work with a pickle file
    arg-attr = pathlib.Path, None: path = None ;
               this argument gives the path of the pickle file used for storing
               datas, so it is unseful if ``mode = "list"``


This class gives an easy way to work either with a pickle file or with a list
so as to store datas. Here is how to use this class.

    1) The context syntax ``with ...:`` opens the IO stream like object.

    2) To add a new data, just use the method  ``write``.

    3) To read the datas, just use the iterator syntax ``for data in ...:``.
    """

    def __init__(self, mode, path = None):
        self.mode = LONG_IO_TYPES.get(mode, mode)
        self.path = path

    def __enter__(self):
        if self.mode == LIST:
            self.datas = []
            self.write = self._writeinlist
            self.iter  = self._iterinlist

        elif self.mode == PICKLE:
            if self.path.is_file():
                self.path.unlink()

            with self.path.open(mode = "ab") as f:
                ...

            self.datas = self.path
            self.write = self._writeinfile
            self.iter  = self._iterinfile

        else:
            raise ValueError("unknown mode.")

    def __exit__(self, type, value, traceback):
        ...

    def _writeinlist(self, value):
        self.datas.append(value)

    def _iterinlist(self):
        for data in self.datas:
            yield data

    def _writeinfile(self, value):
        pickle.dump(value, self.datas.open(mode = "ab"))

    def _iterinfile(self):
        with self.datas.open(mode = "rb") as datas:
            try:
                while True:
                    yield pickle.load(datas)

            except EOFError:
                ...

    def __iter__(self):
        yield from self.iter()

    def remove(self):
        if self.mode != LIST \
        and self.datas.is_file():
            self.datas.unlink()
