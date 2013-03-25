# -*- coding: utf-8 -*-
__author__ = 'maxaon'
from os import listdir, path
from re import match

__all__ = []
for file in listdir(path.dirname(__file__)):
    r = match(r"^([A-Za-z0-9]+[A-Za-z0-9_]*)\.py$", file)
    if r:
        __all__.append(r.group(1))

if __name__ == "__main__":
    pass
