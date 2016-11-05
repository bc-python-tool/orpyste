What about this package  ?
==========================

**orPyste**, which is an anagram of **pyStore**, has been built so as to make easy to work with textual datas easy stored in a text file.

***If you want more informations and examples than thereafter, just take
a look in the docstrings.***


I beg your pardon for my english...
===================================

English is not my native language, so be nice if you notice misunderstandings, misspellings or grammatical errors in my documents and my codes.


Warning about this new version `1.1.0-beta`
==========================================

This version breaks everything regarding to the previous ones. So this is really a new package that still follows the same philosophy than the original project.


Why yet another tiny language to store textual datas ?
======================================================

The package `orpyste` was born from a need to quickly write simple and structured datas to configuration files and for unit tests. Before getting into the details, here is a small example of an `orpyste` file storing informations on players. Sorry for the lack of originality ...


```
joueur_1::
    date  = 1985
    sexe  = masculin
    score = 18974
    alias = Super Mario

joueur_2::
    date  = 1991
    sexe  = féminin
    score = 32007
    alias = Sonic
```

Writing this with XML could be done like this :

```xml
<joueur_1 date="1985" sexe="masculin" score="18974" alias="Super Mario"/>

<joueur_2 date="1991" sexe="féminin" score="32007" alias="Sonic"/>
```

Using JSON, we could use the following variable.

```json
{
    "joueur_1": {
        "date": "1985",
        "sexe": "masculin",
        "score": "18974",
        "alias": "Super Mario",
    },
    "joueur_2": {
        "date": "1991",
        "sexe": "féminin",
        "score": "32007",
        "alias": "Sonic",
    }
}
```

As you can see, for simple datas, `orpyste` gives a very simple and efficient way to store informations.


How to write files readable by `orpyste` ?
==========================================

The specification of the files readeable by `orpyste` is named `peuf`. So the two questions become : *"What is a well formatted `peuf` file ?"*.
To answer this, let's look at the following example.

```
/*
Long comment: here, we use the first block as a container.

Note the use of two consecutive double points so as to indicate a block.
*/  
book::
// Short comment: then the block `general` uses a key-value storing.
    general::
        author = M. Nobody
        title  = Does this book have a title ?
        date   = 2012, May the 1st

// Short comment: the last block `resume` uses a verbatim content.
    resume::
        This book is an ode to the passing time...


////
```


Let's explain the content of the preceding example.

1. You can comment your `peuf` files using C-like comments but **a comment can only start at the very beginning of a line**.

1. Datas are structured in blocks which can be of three different kinds.

  * A block is indicated using two consecutive double points and its content is indented.

  * A block can be a container like the block `book`. This is for gathering different blocks.

  * The block `general` stores key-value datas with the possibility to choose the separators. **Here we have used `=` but it is not an obligation.** You can also choose to allow or not multiple use of the same key.

  * The last kind of blocks is for a verbatim content. The last empty lines are removed except if you use the magic comment `////` as we have done. In our example the block `resume` has a content made of `This book is an ode to the passing time...` followed by two empty lines.


Reading the datas line by line
==============================

Let's consider the following file where `book` is a container, `general` is a classical key-value content using the separator `=` and `resume` has a verbatim content.  

```
book::
    general::
        author = M. Nobody
        title  = Does this book have a title ?
        date   = 2012, May the 1st

    resume::
        This book is an ode to the passing time...
        A challenging thinking.
```


Let's suppose that `user/example.peuf` is the path of our storing file. Using the following code shows how to read our datas *(the last command `datas.remove()` removes intermediate files build by `orpyste`)*.

```python
from pathlib import Path
import pprint

from orpyste.data import Read

datas = Read(
    content = Path("x-debug-x.txt"),
    mode    = {
        "container" : ":default:",
        "keyval:: =": "general",
        "verbatim"  : "resume"
    }
)

datas.build()

for onedata in datas:
    if onedata.isblock():
        print('--- {0} ---'.format(onedata.querypath))
    elif onedata.isdata():
        pprint.pprint(onedata.rtu_data())

datas.remove()
```

Launching in a terminal, the script will produce the following output where you can note that a "querypath" like `book/general` indicates that the block `general` is inside the block `book`.

```
--- book/general ---
('author', '=', 'M. Nobody')
('title', '=', 'Does this book have a title ?')
('date', '=', '2012, May the 1st')
--- book/resume ---
'This book is an ode to the passing time...'
'A challenging thinking.'
```

You can see that verbatim contents are given line by line, and that the separator between one key and its value is always indicated. This last behavior is due to the fact that you can use different separators if you want. Let's see an example of this with the following data file.

```
logic::
    A <==> B
    A ==> B
    A <== P
```

This file is easy to read with the code above where `mode = "multikeyval:: <==> <== ==>"` is a shortcut for `mode = {"multikeyval:: <==> <== ==>": ":default:"}`. This setting allows multiple use of the same key.

```python
from pathlib import Path
import pprint

from orpyste.data import Read

datas = Read(
    content = Path("x-debug-x.txt"),
    mode    = "multikeyval:: <==> <== ==>"
)

datas.build()

for onedata in datas:
    if onedata.isblock():
        print('--- {0} ---'.format(onedata.querypath))
    elif onedata.isdata():
        pprint.pprint(onedata.rtu_data())

datas.remove()
```

The output below shows the necessity to always give the separators.

```
--- logic ---
('A', '<==>', 'B')
('A', '==>', 'B')
('A', '<==', 'P')
```


Reading the datas block by block
================================

We go back to our second example with the following file whose path is `user/example.peuf`.

```
book::
    general::
        author = M. Nobody
        title  = Does this book have a title ?
        date   = 2012, May the 1st

    resume::
        This book is an ode to the passing time...
        A challenging thinking.
```


The class `ReadBlock` is a subclass of `Read` so you can use any methods working with `Read`. But the goal of `ReadBlock` is to work with dictionaries instead of reading datas line by line *(for large files this last choice is a better one)*. Let's see first the method `flatdict`.

```python
from pathlib import Path
import pprint

from orpyste.data import ReadBlock

datas = ReadBlock(
    content = Path("user/example.peuf"),
    mode    = {
        "container" : ":default:",
        "mk:: =": "general",
        "verbatim"  : "resume"
    }
)

datas.build()

print('--- Default ---')
pprint.pprint(datas.flatdict())

print('--- Without the separators ---')
pprint.pprint(datas.flatdict(nosep = True))

datas.remove()
```


The code launched in one terminal gives us the following outputs.

```
--- Default ---
OrderedDict([('book/general',
              OrderedDict([('author', {'sep': '=', 'value': 'M. Nobody'}),
                           ('title',
                            {'sep': '=',
                             'value': 'Does this book have a title ?'}),
                           ('date',
                            {'sep': '=', 'value': '2012, May the 1st'})])),
             ('book/resume',
              ['This book is an ode to the passing time...',
               'A challenging thinking.'])])
--- Without the separators ---
OrderedDict([('book/general',
              OrderedDict([('author', 'M. Nobody'),
                           ('title', 'Does this book have a title ?'),
                           ('date', '2012, May the 1st')])),
             ('book/resume',
              ['This book is an ode to the passing time...',
               'A challenging thinking.'])])
```


As you can see, the keys are "querypaths" and the values are the datas. You can also use the method `recudict` which produces a "recursive" dictionary. The following code is similar to the previous one except the end *(`[...]` indicates the first lines of the preceding code)*.

```python
[...]

datas.build()

print('--- Default ---')
pprint.pprint(datas.recudict())

print('--- Without the separators ---')
pprint.pprint(datas.recudict(nosep = True))

datas.remove()
```


Here are the dictionaries produced *(the structure is similar to the organization of the blocks)*.

```
--- Default ---
OrderedRecuDict([('book',
                  OrderedRecuDict([('general',
                                    OrderedDict([('author',
                                                  {'sep': '=',
                                                   'value': 'M. Nobody'}),
                                                 ('title',
                                                  {'sep': '=',
                                                   'value': 'Does this book '
                                                            'have a title ?'}),
                                                 ('date',
                                                  {'sep': '=',
                                                   'value': '2012, May the '
                                                            '1st'})])),
                                   ('resume',
                                    ['This book is an ode to the passing '
                                     'time...',
                                     'A challenging thinking.'])]))])
--- Without the separators ---
OrderedRecuDict([('book',
                  OrderedRecuDict([('general',
                                    OrderedDict([('author', 'M. Nobody'),
                                                 ('title',
                                                  'Does this book have a title '
                                                  '?'),
                                                 ('date',
                                                  '2012, May the 1st')])),
                                   ('resume',
                                    ['This book is an ode to the passing '
                                     'time...',
                                     'A challenging thinking.'])]))])
```


Searching for blocks
====================

Here we consider the following file whose path remains equal to `user/example.peuf`.

```
main::
    test::
        a = 1 + 9
        b <>  2
        c = 3 and 4

    sub_main::
        sub_sub_main::
            verb::
                line 1
                    line 2
                        line 3
```


The classes `Read` and `ReadBlock` allow to search for data blocks using queries on "querypaths". The special syntax to use tries to catch the best of the Python regex and the Unix-glob syntaxes. Take a look at the documentation of the function ``data.regexify`` for details. The following examples give some examples of queries.

```python
from pathlib import Path

from orpyste.data import Read

datas = Read(
    content = Path("user/example.peuf"),
    mode    = {
        "container"    : ":default:",
        "keyval:: = <>": "test",
        "verbatim"     : "verb"
    }
)

datas.build()

for query in [
    "main/test",    # Only one path
    "**",           # Anything
    "main/*",       # Anything "contained" inside "main"
]:
    title = "Query: {0}".format(query)
    hrule = "="*len(title)

    print("", hrule, title, hrule, sep = "\n")

    for oneinfo in datas[query]:
        if oneinfo.isblock():
            print(
                "",
                "--- {0} [{1}] ---".format(
                    oneinfo.querypath,
                    oneinfo.mode
                ),
                sep = "\n"
            )

        else:
            print(oneinfo.rtu_data())

datas.remove()
```


This gives the following outputs as expected.

```
================
Query: main/test
================

--- main/test [keyval] ---
('a', '=', '1 + 9')
('b', '<>', '2')
('c', '=', '3 and 4')

=========
Query: **
=========

--- main/test [keyval] ---
('a', '=', '1 + 9')
('b', '<>', '2')
('c', '=', '3 and 4')

--- main/sub_main/sub_sub_main/verb [verbatim] ---
line 1
    line 2
        line 3

=============
Query: main/*
=============

--- main/test [keyval] ---
('a', '=', '1 + 9')
('b', '<>', '2')
('c', '=', '3 and 4')
```


Storing your datas in a `json` variable
=======================================

The class ``ReadBlock`` has a method `jsonify` that allows to store your datas in a `json` file *(the storing has to be done by you)*. The following code will give us just after the strucure used.

```python
from orpyste.data import ReadBlock

content = '''
main::
    test::
        a = 1 + 9
        b <>  2
        c = 3 and 4

    sub_main::
        sub_sub_main::
            verb::
                line 1
                    line 2
                        line 3
'''

datas = ReadBlock(
    content = content,
    mode    = {
        "container"    : ":default:",
        "keyval:: = <>": "test",
        "verbatim"     : "verb"
    }
)

datas.build()

jsonobj = datas.jsonify()
print(jsonobj)
```


Launched in a terminal, we obtain the following output which has been hand formatted. As you can see, we use the format `[key, value]` so as to store the keys and the values of the `python` dictionary given by the method `ReadBlock.flatdict`  and `ReadBlock.recudict` .

```
{
    "kind": "flat",
    "datas" : [
        [
            "main/test",
            [
                [
                    "a",
                    [
                        null,
                        {"value": "1 + 9", "sep": "="}
                    ]
                ],
                [
                    "b",
                    [
                        null,
                        {"value": "2", "sep": "<>"}]
                    ],
                [
                    "c",
                    [
                        null,
                        {"value": "3 and 4", "sep": "="}
                    ]
                ]
            ]
        ],
        [
            "main/sub_main/sub_sub_main/verb",
            [
                null,
                ["line 1", "    line 2", "        line 3"]
            ]
        ]
    ]
}
```


You can easily go back to the `python` dictionary thanks to the function `loadjson` that transforms one json variable stored in one string or in a file into a flat or recursive dictionary regarding to the method used ``ReadBlock.flatdict`` or ``ReadBlock.recudict``.