#! /usr/bin/env python3

"""
prototype::
    date = 2017-07-30


This module just adds the possibility to aggregate different virtual ¨peuf files
inside a single physicial one using sections.
"""

from .data import (
    loadjson,
    Read as _data_Read,
    ReadBlock as _data_ReadBlock
)

# Things are easy to do thanks to the OOP !  (:-p)

QPATH_SECTION_TEMPLATE = "<{0}>"

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


info::
    Take first a look at the documentation of the class ``data.Read`` because
    we are going to speek only of the sections.


A section allows to define a kind of virtual peuf file. Here is how to do.
Let's start with a peuf file of "key-value" datas where the sections are
indicated between two lines of at least two signs ``=``.

orpyste::
    ==
    Section A
    ==
    test_1::
        a = 1

    // Beautiful title for a section...
    =========
    Section B
    =========
    test_2::
        b = 2

    test_3::
        c = 3


Let's write a small script to see the "querypaths" and to read the datas "line
by line" using the "rtu" format.

python::
    from orpyste.section import Read

    with ReadBlock(
        content = path_to_peuf_file_above,
        mode    = "keyval:: ="
    ) as datas:
        for onedata in datas:
            if onedata.isblock():
                print('--- {0} ---'.format(onedata.querypath))

            elif onedata.isdata():
                print(onedata.rtu)


Launched in a terminal, the previous ¨python file produces the output above.

term::
    --- <Section A>/test_1 ---
    (5, 'a', '=', '1')
    --- <Section B>/test_2 ---
    (11, 'b', '=', '2')
    --- <Section B>/test_3 ---
    (14, 'c', '=', '3')


As you can see, each section is identified in "querypaths" by being inside
``<...>``. So you can find a section easily. If in the ¨python file above,
we use ``for onedata in datas["<*B>**"]:...`` instead of ``for onedata in
datas:...``, we obtain the following output.

term::
    --- <Section B>/test_2 ---
    (11, 'b', '=', '2')
    --- <Section B>/test_3 ---
    (14, 'c', '=', '3')
    """
    ...


class ReadBlock(_SectionRead, _data_ReadBlock):
    """
prototype::
    see = data.Read , _SectionRead


info::
    Just take a look at the documentations of the classes ``data.ReadBlock``
    and ``section.ReadBlock``.
    """
    ...
