# #!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <andrew.w.gross@gmail.com> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet
# some day, and you think this stuff is worth it, you can buy me a
# beer in return Poul-Henning Kamp
# ----------------------------------------------------------------------------

import os
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('pyrelic'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

setup(name='pyrelic',
    version='0.2.0',
    description='New Relic Python API Client',
    author=u'Andrew Gross',
    author_email='andrew.w.gross@gmail.com',
    url='http://github.com/andrewgross/pyrelic',
    packages=['pyrelic'],
    install_requires=[
        "lxml", "requests"
    ],
    
)
