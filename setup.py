# ------------------------------------------------ #
# -- LINE COMMANDS FOR TWINE (which uses HTTPS) -- #
# ------------------------------------------------ #

# Source: https://pypi.python.org/pypi/twine

#     1) Create some distributions in the normal way:
#         > python setup.py sdist bdist_wheel
#
#     2) Upload with twine:
#         > twine upload dist/* --skip-existing


# -------------------- #
# -- STANDARD TOOLS -- #
# -------------------- #

from setuptools import setup, find_packages
from pathlib import Path
import pypandoc


# ----------------- #
# -- README FILE -- #
# ----------------- #

READ_ME_FILE = Path(__file__).parent / 'README.md'

with READ_ME_FILE.open(
    mode     = "r",
    encoding = "utf-8"
) as file:
    longdesc = file.read()


# ----------------- #
# -- OUR SETTNGS -- #
# ----------------- #

setup(
# General
    name         = "orpyste",
    version      = "1.3.1-beta",
    url          = 'https://github.com/bc-python/orpyste',
    license      = 'GPLv3',
    author       = "Christophe BAL",
    author_email = "projetmbc@gmail.com",

# Descritions
    long_description              = longdesc,
    long_description_content_type = "text/markdown",
    description                   = "orPyste is a tool to store and read simple structured datas in TXT files using a human efficient syntax.",

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
