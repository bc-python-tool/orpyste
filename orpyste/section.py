#! /usr/bin/env python3

"""
prototype::
    date = 2017-04-22


This module adds the possibility to aggregate different virtual ¨peuf files
inside a single physicial one using sections.
"""

from .data import (
    Read as _data_Read,
    ReadBlock as _data_ReadBlock
)

# Things are easy to do thanks to the OOP !  (:-p)

QPATH_SECTION_TEMPLATE = "[{0}]"

class _SectionRead():
    """
prototype::
    see = data.Read
    """
# << Warning ! >> the class ``data.Read`` disallows the sections.
    def open_section(self):
        ...

    def section_title(self, title):
        self._qpath = [QPATH_SECTION_TEMPLATE.format(title)]


class Read(_SectionRead, _data_Read):
    """
prototype::
    see = data.Read , _SectionRead
    """
    ...


class ReadBlock(_SectionRead, _data_ReadBlock):
    """
prototype::
    see = data.Read , _SectionRead
    """
    ...
