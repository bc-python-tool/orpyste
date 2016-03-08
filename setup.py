from setuptools import setup, find_packages
from pathlib import Path

readme = Path(__file__).parent / 'README.md'

with readme.open(encoding='utf-8') as f:
    longdesc = f.read()


setup(
# General
    name         = "orpyste",
    version      = "1.0.0",
    url          = 'https://github.com/bc-python-tools/orpyste',
    license      = 'GPLv3',
    author       = "Christophe BAL",
    author_email = "projetmbc@gmail.com",

# Descritions
    description      = "orPyste is a tool to store and read datas in TXT files using a human efficient syntax.",
    long_description = longdesc,

# What to add ?
    packages = find_packages(),

# Uggly classifiers
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

# What does your project relate to?
    keywords = 'python data',
)
