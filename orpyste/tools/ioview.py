#! /usr/bin/env python3

"""
prototype::
    date = 2015-07-03


This module gives an easy way to work either with a pickle file or with a list
so as to store and read datas.
"""

import pickle


class IOView():
    """
prototype::
    arg-attr = str: mode in self.MODES
                         or in self.LONG_MODES ;
               if ``mode = "list"`` then you will work with a list, and if
               ``mode = "pickle"`` then you will work with a pickle file
    arg-attr = pathlib.Path, None: path = None ;
               this argument gives the path of the pickle file used for storing
               datas, so it is unseful if ``mode = "list"``


This class gives an easy way to work either with a pickle file or with a list so
as to store datas. Herer is how to use this class.

    1) The context syntax ``with ...:`` opens the IO stream like object.

    2) To add a new data, just use the method  ``write``.

    3) To read the datas, just use the iterator syntax ``for data in ...:``.
    """
    LIST, PICKLE = "list", "pickle"

    MODES      = [LIST, PICKLE]
    LONG_MODES = {x[0]: x for x in MODES}


    def __init__(self, mode, path = None):
        self.mode = self.LONG_MODES.get(mode, mode)
        self.path = path


    def __enter__(self):
        if self.mode == self.LIST:
            self._datas = []
            self.write  = self._writeinlist

        elif self.mode == self.PICKLE:
            self._datas = self.path.open(mode = "w")
            self.write  = self._writeinfile

        else:
            raise ValueError("unknown mode.")


    def __exit__(self, type, value, traceback):
        if self.mode == self.PICKLE:
            self._datas.close()


    def _writeinlist(self, value):
        self._datas.append(value)


    def _writeinfile(self, value):
        pickle.dump(value, self._datas)


    def __iter__(self):
        if self.mode == self.LIST:
            for data in self._datas:
                yield data

        else:
            try:
                while True:
                    yield pickle.load(self._datas)

            except EOFError:
                pass
